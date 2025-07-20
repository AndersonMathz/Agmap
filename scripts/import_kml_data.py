#!/usr/bin/env python3
"""
WEBAG - Importador de Dados KML
Script para importar dados KML para o banco
"""
import sqlite3
import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime

def parse_kml_file(kml_path):
    """Parse básico de arquivo KML"""
    try:
        tree = ET.parse(kml_path)
        root = tree.getroot()
        
        # Namespace do KML
        ns = {'kml': 'http://www.opengis.net/kml/2.2'}
        
        features = []
        
        # Buscar placemarks
        for placemark in root.findall('.//kml:Placemark', ns):
            feature = {}
            
            # Nome
            name_elem = placemark.find('kml:name', ns)
            if name_elem is not None:
                feature['name'] = name_elem.text
            
            # Descrição
            desc_elem = placemark.find('kml:description', ns)
            if desc_elem is not None:
                feature['description'] = desc_elem.text
            
            # Geometria (simplificada)
            point = placemark.find('.//kml:Point/kml:coordinates', ns)
            if point is not None:
                coords = point.text.strip().split(',')
                if len(coords) >= 2:
                    feature['geometry'] = {
                        'type': 'Point',
                        'coordinates': [float(coords[0]), float(coords[1])]
                    }
            
            polygon = placemark.find('.//kml:Polygon', ns)
            if polygon is not None:
                feature['geometry'] = {
                    'type': 'Polygon',
                    'coordinates': 'complex_polygon_data'  # Simplificado
                }
            
            linestring = placemark.find('.//kml:LineString', ns)
            if linestring is not None:
                feature['geometry'] = {
                    'type': 'LineString', 
                    'coordinates': 'complex_line_data'  # Simplificado
                }
            
            if feature:
                features.append(feature)
        
        return features
        
    except Exception as e:
        print(f"❌ Erro parseando {kml_path}: {e}")
        return []

def import_features_to_db(db_path, features, layer_name, project_id):
    """Importa features para o banco"""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            imported = 0
            for feature in features:
                properties = {
                    'name': feature.get('name', 'Sem nome'),
                    'description': feature.get('description', ''),
                    'imported_from': layer_name
                }
                
                cursor.execute("""
                    INSERT INTO geo_features 
                    (project_id, layer_name, feature_type, geometry, properties)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    project_id,
                    layer_name,
                    feature.get('geometry', {}).get('type', 'Unknown'),
                    json.dumps(feature.get('geometry', {})),
                    json.dumps(properties)
                ))
                imported += 1
            
            print(f"✅ Importadas {imported} features de {layer_name}")
            return imported
            
    except Exception as e:
        print(f"❌ Erro importando para banco: {e}")
        return 0

def get_project_id(db_path):
    """Obtém ID do projeto exemplo"""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM projects WHERE name = 'Projeto Exemplo'")
            result = cursor.fetchone()
            return result[0] if result else None
    except:
        return None

def main():
    """Função principal"""
    print("=== WEBAG KML Data Importer ===")
    
    db_path = "instance/webgis.db"
    kml_dir = "WEBGIS_ANDERSON"
    
    # Verificar banco
    if not os.path.exists(db_path):
        print(f"❌ Banco não encontrado: {db_path}")
        return 1
    
    # Obter projeto
    project_id = get_project_id(db_path)
    if not project_id:
        print("❌ Projeto exemplo não encontrado")
        return 1
    
    print(f"📁 Usando projeto ID: {project_id}")
    
    # KML files para importar
    kml_files = [
        ('building.kml', 'Edifícios'),
        ('roads.kml', 'Estradas'),
        ('places.kml', 'Lugares'),
        ('ma_setores_2021.kml', 'Setores Censitários')
    ]
    
    total_imported = 0
    
    for kml_file, layer_name in kml_files:
        kml_path = os.path.join(kml_dir, kml_file)
        
        if os.path.exists(kml_path):
            print(f"📄 Processando {kml_file}...")
            features = parse_kml_file(kml_path)
            
            if features:
                imported = import_features_to_db(db_path, features, layer_name, project_id)
                total_imported += imported
            else:
                print(f"⚠️  Nenhuma feature encontrada em {kml_file}")
        else:
            print(f"⚠️  Arquivo não encontrado: {kml_path}")
    
    print(f"\n🎉 Importação concluída: {total_imported} features totais")
    
    # Verificar resultado
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM geo_features")
            total = cursor.fetchone()[0]
            print(f"📊 Total de features no banco: {total}")
    except Exception as e:
        print(f"❌ Erro verificando resultado: {e}")
    
    return 0

if __name__ == "__main__":
    exit(main())