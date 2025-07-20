import os
import json
import xml.etree.ElementTree as ET
from app import create_app, db
from models import GeoFeature

# Estrutura de propriedades padrão
def get_default_properties():
    return {
        "no_gleba": "",
        "nome_gleba": "",
        "area": "",
        "perimetro": "",
        "proprietario_nome": "",
        "cpf": "",
        "rg": "",
        "rua": "",
        "bairro": "",
        "quadra": "",
        "cep": "",
        "cidade": "",
        "uf": "",
        "testada_frente": "",
        "testada_ld": "",
        "testada_le": "",
        "testada_f": "",
        "matricula": "",
        "classe_imovel": "Urbano",
        "tipo_imovel": "Residencial",
        "descricao_imovel": ""
    }

def parse_kml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    namespace = {'kml': 'http://www.opengis.net/kml/2.2'}
    features = []

    for placemark in root.findall('.//kml:Placemark', namespace):
        properties = get_default_properties()
        name_element = placemark.find('kml:name', namespace)
        if name_element is not None:
            properties['nome_gleba'] = name_element.text

        # Extrair geometria (Polygon)
        try:
            coords_text = placemark.find('.//kml:coordinates', namespace).text.strip()
            coords_list = [item.split(',')[:2] for item in coords_text.split()] 
            coords_float = [[float(lon), float(lat)] for lon, lat in coords_list]
            
            geometry = {
                "type": "Polygon",
                "coordinates": [coords_float]
            }
            features.append({
                "geometry": geometry,
                "properties": properties
            })
        except (AttributeError, IndexError, ValueError) as e:
            print(f"Erro ao processar geometria para um Placemark em {os.path.basename(file_path)}: {e}")
            continue

    return features

def main():
    app = create_app()
    with app.app_context():
        # Limpar dados existentes
        db.session.query(GeoFeature).delete()
        db.session.commit()
        print("Tabela GeoFeature limpa.")

        kml_dir = 'WEBGIS_ANDERSON'
        for filename in os.listdir(kml_dir):
            if filename.endswith('.kml'):
                file_path = os.path.join(kml_dir, filename)
                print(f"Processando arquivo: {filename}")
                layer_name = os.path.splitext(filename)[0]
                features_data = parse_kml(file_path)

                for data in features_data:
                    new_feature = GeoFeature(
                        layer_name=layer_name,
                        geometry=data['geometry'],
                        properties=data['properties']
                    )
                    db.session.add(new_feature)
        
        db.session.commit()
        print("Dados importados com sucesso para o banco de dados!")

if __name__ == '__main__':
    main()
