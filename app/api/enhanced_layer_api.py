"""
WEBAG Professional - Enhanced Layer Management API
APIs REST avançadas para gestão robusta de camadas
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from flask import Blueprint, request, jsonify, current_app
from werkzeug.exceptions import BadRequest, NotFound, Forbidden

# Imports do sistema enhanced
try:
    from app.models.enhanced_models import (
        db, Organization, User, Project, LayerGroup, Layer, Feature, 
        Gleba, AuditLog, LayerVersion, LayerType, GeometryType, StatusType
    )
    ENHANCED_MODELS_AVAILABLE = True
except ImportError:
    ENHANCED_MODELS_AVAILABLE = False

# Imports para autenticação
try:
    from flask_login import login_required, current_user
    FLASK_LOGIN_AVAILABLE = True
except ImportError:
    FLASK_LOGIN_AVAILABLE = False

# ================================================
# BLUEPRINT SETUP
# ================================================

layer_api = Blueprint('layer_api', __name__, url_prefix='/api/v2')

def requires_auth(f):
    """Decorator para autenticação"""
    def decorated_function(*args, **kwargs):
        if not FLASK_LOGIN_AVAILABLE or not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def log_action(action: str, resource_type: str, resource_id: str, 
               old_values: Dict = None, new_values: Dict = None):
    """Log de auditoria"""
    if not ENHANCED_MODELS_AVAILABLE:
        return
    
    try:
        changed_fields = []
        if old_values and new_values:
            changed_fields = [k for k in new_values.keys() 
                            if k in old_values and old_values[k] != new_values[k]]
        
        audit_log = AuditLog(
            table_name=resource_type,
            record_id=resource_id,
            operation=action,
            old_values=old_values,
            new_values=new_values,
            changed_fields=changed_fields,
            user_id=current_user.id if FLASK_LOGIN_AVAILABLE and current_user.is_authenticated else None,
            user_ip=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        db.session.add(audit_log)
        db.session.commit()
        
    except Exception as e:
        current_app.logger.error(f"Erro no log de auditoria: {e}")

# ================================================
# LAYER GROUP MANAGEMENT
# ================================================

@layer_api.route('/projects/<project_id>/layer-groups', methods=['GET'])
@requires_auth
def get_layer_groups(project_id: str):
    """Obter grupos de camadas de um projeto"""
    try:
        # Verificar se projeto existe e usuário tem acesso
        project = Project.query.filter_by(
            id=project_id,
            organization_id=current_user.organization_id
        ).first()
        
        if not project:
            return jsonify({'error': 'Projeto não encontrado'}), 404
        
        # Obter grupos hierárquicos
        groups = LayerGroup.query.filter_by(
            project_id=project_id,
            parent_group_id=None
        ).order_by(LayerGroup.display_order).all()
        
        def build_group_tree(group):
            """Construir árvore hierárquica de grupos"""
            children = LayerGroup.query.filter_by(
                parent_group_id=group.id
            ).order_by(LayerGroup.display_order).all()
            
            layers = Layer.query.filter_by(
                layer_group_id=group.id
            ).order_by(Layer.display_order).all()
            
            return {
                **group.to_dict(),
                'children': [build_group_tree(child) for child in children],
                'layers': [layer.to_dict() for layer in layers]
            }
        
        result = [build_group_tree(group) for group in groups]
        
        return jsonify({
            'layer_groups': result,
            'project_id': project_id,
            'total': len(result)
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro obtendo grupos: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@layer_api.route('/projects/<project_id>/layer-groups', methods=['POST'])
@requires_auth
def create_layer_group(project_id: str):
    """Criar novo grupo de camadas"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados obrigatórios'}), 400
        
        # Validações
        if not data.get('name'):
            return jsonify({'error': 'Nome do grupo é obrigatório'}), 400
        
        # Verificar projeto
        project = Project.query.filter_by(
            id=project_id,
            organization_id=current_user.organization_id
        ).first()
        
        if not project:
            return jsonify({'error': 'Projeto não encontrado'}), 404
        
        # Verificar permissões
        if not current_user.has_privilege('canManageLayers'):
            return jsonify({'error': 'Sem permissão para gerenciar camadas'}), 403
        
        # Criar grupo
        group = LayerGroup(
            project_id=project_id,
            parent_group_id=data.get('parent_group_id'),
            name=data['name'],
            description=data.get('description'),
            display_order=data.get('display_order', 0),
            is_expanded=data.get('is_expanded', True),
            is_visible=data.get('is_visible', True)
        )
        
        db.session.add(group)
        db.session.commit()
        
        # Log da ação
        log_action('INSERT', 'layer_groups', group.id, None, group.to_dict())
        
        return jsonify({
            'message': 'Grupo criado com sucesso',
            'group': group.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro criando grupo: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@layer_api.route('/layer-groups/<group_id>', methods=['PUT'])
@requires_auth
def update_layer_group(group_id: str):
    """Atualizar grupo de camadas"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados obrigatórios'}), 400
        
        # Buscar grupo
        group = LayerGroup.query.join(Project).filter(
            LayerGroup.id == group_id,
            Project.organization_id == current_user.organization_id
        ).first()
        
        if not group:
            return jsonify({'error': 'Grupo não encontrado'}), 404
        
        # Verificar permissões
        if not current_user.has_privilege('canManageLayers'):
            return jsonify({'error': 'Sem permissão para gerenciar camadas'}), 403
        
        # Salvar valores antigos para auditoria
        old_values = group.to_dict()
        
        # Atualizar campos
        updatable_fields = [
            'name', 'description', 'display_order', 
            'is_expanded', 'is_visible', 'parent_group_id'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(group, field, data[field])
        
        db.session.commit()
        
        # Log da ação
        log_action('UPDATE', 'layer_groups', group_id, old_values, group.to_dict())
        
        return jsonify({
            'message': 'Grupo atualizado com sucesso',
            'group': group.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro atualizando grupo: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@layer_api.route('/layer-groups/<group_id>', methods=['DELETE'])
@requires_auth
def delete_layer_group(group_id: str):
    """Deletar grupo de camadas"""
    try:
        # Buscar grupo
        group = LayerGroup.query.join(Project).filter(
            LayerGroup.id == group_id,
            Project.organization_id == current_user.organization_id
        ).first()
        
        if not group:
            return jsonify({'error': 'Grupo não encontrado'}), 404
        
        # Verificar permissões
        if not current_user.has_privilege('canDeleteLayers'):
            return jsonify({'error': 'Sem permissão para deletar'}), 403
        
        # Verificar se tem layers ou subgrupos
        has_layers = Layer.query.filter_by(layer_group_id=group_id).first() is not None
        has_children = LayerGroup.query.filter_by(parent_group_id=group_id).first() is not None
        
        if has_layers or has_children:
            return jsonify({
                'error': 'Grupo contém camadas ou subgrupos. Mova ou delete primeiro.'
            }), 400
        
        # Salvar para auditoria
        old_values = group.to_dict()
        
        # Deletar
        db.session.delete(group)
        db.session.commit()
        
        # Log da ação
        log_action('DELETE', 'layer_groups', group_id, old_values, None)
        
        return jsonify({'message': 'Grupo deletado com sucesso'})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro deletando grupo: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

# ================================================
# LAYER MANAGEMENT
# ================================================

@layer_api.route('/projects/<project_id>/layers', methods=['GET'])
@requires_auth
def get_layers(project_id: str):
    """Obter camadas de um projeto"""
    try:
        # Verificar projeto
        project = Project.query.filter_by(
            id=project_id,
            organization_id=current_user.organization_id
        ).first()
        
        if not project:
            return jsonify({'error': 'Projeto não encontrado'}), 404
        
        # Filtros opcionais
        layer_type = request.args.get('type')
        status = request.args.get('status', 'active')
        group_id = request.args.get('group_id')
        
        # Query base
        query = Layer.query.filter_by(project_id=project_id)
        
        # Aplicar filtros
        if layer_type:
            try:
                query = query.filter_by(layer_type=LayerType(layer_type))
            except ValueError:
                return jsonify({'error': f'Tipo de camada inválido: {layer_type}'}), 400
        
        if status:
            try:
                query = query.filter_by(status=StatusType(status))
            except ValueError:
                return jsonify({'error': f'Status inválido: {status}'}), 400
        
        if group_id:
            query = query.filter_by(layer_group_id=group_id)
        
        # Ordenação
        layers = query.order_by(Layer.display_order, Layer.name).all()
        
        # Serializar com informações adicionais
        result = []
        for layer in layers:
            layer_dict = layer.to_dict()
            layer_dict['feature_count'] = layer.feature_count
            layer_dict['group_name'] = layer.layer_group.name if layer.layer_group else None
            layer_dict['creator_name'] = layer.creator.full_name if layer.creator else None
            result.append(layer_dict)
        
        return jsonify({
            'layers': result,
            'project_id': project_id,
            'total': len(result),
            'filters': {
                'type': layer_type,
                'status': status,
                'group_id': group_id
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro obtendo camadas: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@layer_api.route('/projects/<project_id>/layers', methods=['POST'])
@requires_auth
def create_layer(project_id: str):
    """Criar nova camada"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados obrigatórios'}), 400
        
        # Validações obrigatórias
        required_fields = ['name', 'display_name', 'layer_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo obrigatório: {field}'}), 400
        
        # Verificar projeto
        project = Project.query.filter_by(
            id=project_id,
            organization_id=current_user.organization_id
        ).first()
        
        if not project:
            return jsonify({'error': 'Projeto não encontrado'}), 404
        
        # Verificar permissões
        if not current_user.has_privilege('canAddNewLayers'):
            return jsonify({'error': 'Sem permissão para criar camadas'}), 403
        
        # Validar tipo de camada
        try:
            layer_type = LayerType(data['layer_type'])
        except ValueError:
            return jsonify({'error': f'Tipo de camada inválido: {data["layer_type"]}'}), 400
        
        # Validar tipo de geometria (se fornecido)
        geometry_type = None
        if data.get('geometry_type'):
            try:
                geometry_type = GeometryType(data['geometry_type'])
            except ValueError:
                return jsonify({'error': f'Tipo de geometria inválido: {data["geometry_type"]}'}), 400
        
        # Verificar se nome já existe no projeto
        existing = Layer.query.filter_by(
            project_id=project_id,
            name=data['name']
        ).first()
        
        if existing:
            return jsonify({'error': 'Nome de camada já existe neste projeto'}), 400
        
        # Criar camada
        layer = Layer(
            project_id=project_id,
            layer_group_id=data.get('layer_group_id'),
            name=data['name'],
            display_name=data['display_name'],
            description=data.get('description'),
            layer_type=layer_type,
            geometry_type=geometry_type,
            source_type=data.get('source_type', 'internal'),
            source_url=data.get('source_url'),
            source_config=data.get('source_config', {}),
            default_style=data.get('default_style', {}),
            min_zoom=data.get('min_zoom', 0),
            max_zoom=data.get('max_zoom', 18),
            opacity=data.get('opacity', 1.0),
            srid=data.get('srid', 'EPSG:4326'),
            schema_definition=data.get('schema_definition', {}),
            is_public=data.get('is_public', False),
            is_editable=data.get('is_editable', True),
            is_deletable=data.get('is_deletable', True),
            edit_permissions=data.get('edit_permissions', {}),
            display_order=data.get('display_order', 0),
            is_visible=data.get('is_visible', True),
            is_selectable=data.get('is_selectable', True),
            created_by=current_user.id
        )
        
        db.session.add(layer)
        db.session.commit()
        
        # Criar primeira versão
        if data.get('create_initial_version', True):
            version = layer.create_version(
                version_name='Versão Inicial',
                description='Versão inicial da camada',
                user=current_user
            )
            db.session.add(version)
            db.session.commit()
        
        # Log da ação
        log_action('INSERT', 'layers', layer.id, None, layer.to_dict())
        
        return jsonify({
            'message': 'Camada criada com sucesso',
            'layer': layer.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro criando camada: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@layer_api.route('/layers/<layer_id>', methods=['GET'])
@requires_auth
def get_layer(layer_id: str):
    """Obter detalhes de uma camada específica"""
    try:
        # Buscar camada
        layer = Layer.query.join(Project).filter(
            Layer.id == layer_id,
            Project.organization_id == current_user.organization_id
        ).first()
        
        if not layer:
            return jsonify({'error': 'Camada não encontrada'}), 404
        
        # Verificar se é pública ou se usuário tem acesso
        if not layer.is_public and not current_user.has_privilege('canViewAllData'):
            return jsonify({'error': 'Sem permissão para visualizar esta camada'}), 403
        
        # Obter informações detalhadas
        layer_dict = layer.to_dict()
        
        # Adicionar estatísticas
        layer_dict['statistics'] = {
            'feature_count': layer.feature_count,
            'active_features': Feature.query.filter_by(
                layer_id=layer_id, 
                status=StatusType.ACTIVE, 
                is_current=True
            ).count(),
            'last_updated': layer.updated_at.isoformat() if layer.updated_at else None,
            'version_count': layer.versions.count()
        }
        
        # Adicionar informações do grupo
        if layer.layer_group:
            layer_dict['group'] = {
                'id': layer.layer_group.id,
                'name': layer.layer_group.name,
                'description': layer.layer_group.description
            }
        
        # Adicionar informações do criador
        if layer.creator:
            layer_dict['creator'] = {
                'id': layer.creator.id,
                'name': layer.creator.full_name,
                'username': layer.creator.username
            }
        
        return jsonify({
            'layer': layer_dict
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro obtendo camada: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@layer_api.route('/layers/<layer_id>', methods=['PUT'])
@requires_auth
def update_layer(layer_id: str):
    """Atualizar camada"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados obrigatórios'}), 400
        
        # Buscar camada
        layer = Layer.query.join(Project).filter(
            Layer.id == layer_id,
            Project.organization_id == current_user.organization_id
        ).first()
        
        if not layer:
            return jsonify({'error': 'Camada não encontrada'}), 404
        
        # Verificar permissões
        if not layer.can_edit(current_user):
            return jsonify({'error': 'Sem permissão para editar esta camada'}), 403
        
        # Salvar valores antigos
        old_values = layer.to_dict()
        
        # Campos atualizáveis
        updatable_fields = [
            'display_name', 'description', 'layer_group_id', 'source_url',
            'source_config', 'default_style', 'min_zoom', 'max_zoom', 'opacity',
            'schema_definition', 'is_public', 'is_editable', 'is_deletable',
            'edit_permissions', 'display_order', 'is_visible', 'is_selectable'
        ]
        
        # Validar e aplicar mudanças
        for field in updatable_fields:
            if field in data:
                value = data[field]
                
                # Validações específicas
                if field == 'opacity' and not 0 <= value <= 1:
                    return jsonify({'error': 'Opacidade deve estar entre 0 e 1'}), 400
                
                setattr(layer, field, value)
        
        # Campos especiais que podem mudar tipo
        if 'layer_type' in data:
            try:
                layer.layer_type = LayerType(data['layer_type'])
            except ValueError:
                return jsonify({'error': f'Tipo de camada inválido: {data["layer_type"]}'}), 400
        
        if 'geometry_type' in data:
            try:
                layer.geometry_type = GeometryType(data['geometry_type'])
            except ValueError:
                return jsonify({'error': f'Tipo de geometria inválido: {data["geometry_type"]}'}), 400
        
        if 'status' in data:
            try:
                layer.status = StatusType(data['status'])
            except ValueError:
                return jsonify({'error': f'Status inválido: {data["status"]}'}), 400
        
        # Atualizar updated_by
        layer.updated_by = current_user.id
        
        db.session.commit()
        
        # Criar versão se solicitado
        if data.get('create_version'):
            version = layer.create_version(
                version_name=data.get('version_name', f'Versão {datetime.now().strftime("%Y%m%d_%H%M")}'),
                description=data.get('version_description', 'Atualização da camada'),
                user=current_user
            )
            db.session.add(version)
            db.session.commit()
        
        # Log da ação
        log_action('UPDATE', 'layers', layer_id, old_values, layer.to_dict())
        
        return jsonify({
            'message': 'Camada atualizada com sucesso',
            'layer': layer.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro atualizando camada: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@layer_api.route('/layers/<layer_id>', methods=['DELETE'])
@requires_auth
def delete_layer(layer_id: str):
    """Deletar camada"""
    try:
        # Buscar camada
        layer = Layer.query.join(Project).filter(
            Layer.id == layer_id,
            Project.organization_id == current_user.organization_id
        ).first()
        
        if not layer:
            return jsonify({'error': 'Camada não encontrada'}), 404
        
        # Verificar se é deletável
        if not layer.is_deletable:
            return jsonify({'error': 'Camada não pode ser deletada'}), 400
        
        # Verificar permissões
        if not current_user.has_privilege('canDeleteLayers') and layer.created_by != current_user.id:
            return jsonify({'error': 'Sem permissão para deletar esta camada'}), 403
        
        # Verificar modo de deleção
        soft_delete = request.args.get('soft', 'true').lower() == 'true'
        
        old_values = layer.to_dict()
        
        if soft_delete:
            # Soft delete - apenas marcar como deleted
            layer.status = StatusType.DELETED
            layer.updated_by = current_user.id
            db.session.commit()
            
            message = 'Camada marcada como deletada'
            
        else:
            # Hard delete - remover completamente
            # Primeiro remover features associadas
            Feature.query.filter_by(layer_id=layer_id).delete()
            
            # Remover versões
            LayerVersion.query.filter_by(layer_id=layer_id).delete()
            
            # Remover a camada
            db.session.delete(layer)
            db.session.commit()
            
            message = 'Camada deletada permanentemente'
        
        # Log da ação
        log_action('DELETE', 'layers', layer_id, old_values, None)
        
        return jsonify({'message': message})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro deletando camada: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

# ================================================
# LAYER VERSIONING
# ================================================

@layer_api.route('/layers/<layer_id>/versions', methods=['GET'])
@requires_auth
def get_layer_versions(layer_id: str):
    """Obter versões de uma camada"""
    try:
        # Verificar acesso à camada
        layer = Layer.query.join(Project).filter(
            Layer.id == layer_id,
            Project.organization_id == current_user.organization_id
        ).first()
        
        if not layer:
            return jsonify({'error': 'Camada não encontrada'}), 404
        
        # Obter versões
        versions = LayerVersion.query.filter_by(
            layer_id=layer_id
        ).order_by(LayerVersion.version_number.desc()).all()
        
        result = []
        for version in versions:
            version_dict = version.to_dict()
            version_dict['creator_name'] = version.creator.full_name if version.creator else None
            result.append(version_dict)
        
        return jsonify({
            'versions': result,
            'layer_id': layer_id,
            'total': len(result)
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro obtendo versões: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@layer_api.route('/layers/<layer_id>/versions', methods=['POST'])
@requires_auth
def create_layer_version(layer_id: str):
    """Criar nova versão de uma camada"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados obrigatórios'}), 400
        
        # Buscar camada
        layer = Layer.query.join(Project).filter(
            Layer.id == layer_id,
            Project.organization_id == current_user.organization_id
        ).first()
        
        if not layer:
            return jsonify({'error': 'Camada não encontrada'}), 404
        
        # Verificar permissões
        if not layer.can_edit(current_user):
            return jsonify({'error': 'Sem permissão para versionar esta camada'}), 403
        
        # Criar versão
        version = layer.create_version(
            version_name=data.get('version_name', f'Versão {datetime.now().strftime("%Y%m%d_%H%M")}'),
            description=data.get('description', ''),
            user=current_user
        )
        
        db.session.add(version)
        db.session.commit()
        
        # Log da ação
        log_action('INSERT', 'layer_versions', version.id, None, version.to_dict())
        
        return jsonify({
            'message': 'Versão criada com sucesso',
            'version': version.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro criando versão: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

# ================================================
# LAYER STYLES
# ================================================

@layer_api.route('/layers/<layer_id>/style', methods=['GET'])
@requires_auth
def get_layer_style(layer_id: str):
    """Obter estilo de uma camada"""
    try:
        layer = Layer.query.join(Project).filter(
            Layer.id == layer_id,
            Project.organization_id == current_user.organization_id
        ).first()
        
        if not layer:
            return jsonify({'error': 'Camada não encontrada'}), 404
        
        return jsonify({
            'layer_id': layer_id,
            'style': layer.get_default_style(),
            'opacity': layer.opacity,
            'min_zoom': layer.min_zoom,
            'max_zoom': layer.max_zoom
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro obtendo estilo: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@layer_api.route('/layers/<layer_id>/style', methods=['PUT'])
@requires_auth
def update_layer_style(layer_id: str):
    """Atualizar estilo de uma camada"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados obrigatórios'}), 400
        
        layer = Layer.query.join(Project).filter(
            Layer.id == layer_id,
            Project.organization_id == current_user.organization_id
        ).first()
        
        if not layer:
            return jsonify({'error': 'Camada não encontrada'}), 404
        
        # Verificar permissões
        if not current_user.has_privilege('canModifyStyles') and layer.created_by != current_user.id:
            return jsonify({'error': 'Sem permissão para modificar estilos'}), 403
        
        # Atualizar estilo
        if 'style' in data:
            layer.default_style = data['style']
        
        if 'opacity' in data:
            if not 0 <= data['opacity'] <= 1:
                return jsonify({'error': 'Opacidade deve estar entre 0 e 1'}), 400
            layer.opacity = data['opacity']
        
        if 'min_zoom' in data:
            layer.min_zoom = data['min_zoom']
        
        if 'max_zoom' in data:
            layer.max_zoom = data['max_zoom']
        
        layer.updated_by = current_user.id
        db.session.commit()
        
        return jsonify({
            'message': 'Estilo atualizado com sucesso',
            'style': layer.get_default_style()
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro atualizando estilo: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

# ================================================
# LAYER STATISTICS
# ================================================

@layer_api.route('/layers/<layer_id>/statistics', methods=['GET'])
@requires_auth
def get_layer_statistics(layer_id: str):
    """Obter estatísticas detalhadas de uma camada"""
    try:
        layer = Layer.query.join(Project).filter(
            Layer.id == layer_id,
            Project.organization_id == current_user.organization_id
        ).first()
        
        if not layer:
            return jsonify({'error': 'Camada não encontrada'}), 404
        
        # Estatísticas de features
        total_features = Feature.query.filter_by(layer_id=layer_id).count()
        active_features = Feature.query.filter_by(
            layer_id=layer_id, 
            status=StatusType.ACTIVE,
            is_current=True
        ).count()
        
        # Estatísticas por tipo de geometria
        geometry_stats = {}
        for geom_type in GeometryType:
            count = Feature.query.filter_by(
                layer_id=layer_id,
                feature_type=geom_type,
                is_current=True
            ).count()
            if count > 0:
                geometry_stats[geom_type.value] = count
        
        # Estatísticas temporais
        from sqlalchemy import func
        creation_stats = db.session.query(
            func.date(Feature.created_at).label('date'),
            func.count(Feature.id).label('count')
        ).filter_by(layer_id=layer_id).group_by(
            func.date(Feature.created_at)
        ).order_by('date').limit(30).all()
        
        return jsonify({
            'layer_id': layer_id,
            'statistics': {
                'total_features': total_features,
                'active_features': active_features,
                'deleted_features': total_features - active_features,
                'geometry_types': geometry_stats,
                'creation_timeline': [
                    {'date': str(stat.date), 'count': stat.count}
                    for stat in creation_stats
                ],
                'last_updated': layer.updated_at.isoformat() if layer.updated_at else None,
                'file_size_bytes': layer.file_size_bytes,
                'version_count': layer.versions.count()
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro obtendo estatísticas: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

# ================================================
# ERROR HANDLERS
# ================================================

@layer_api.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Recurso não encontrado'}), 404

@layer_api.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Requisição inválida'}), 400

@layer_api.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Acesso negado'}), 403

@layer_api.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Erro interno do servidor'}), 500