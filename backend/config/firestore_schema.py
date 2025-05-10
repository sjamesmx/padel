"""
Esquema de la base de datos Firestore para Padelyzer.
"""

from datetime import datetime

COLLECTIONS = {
    'users': {
        'fields': {
            'email': str,
            'fecha_registro': (datetime, type(None)),
            'nivel': str,
            'posicion_preferida': str,
            'ultimo_analisis': (str, type(None)),
            'tipo_ultimo_analisis': (str, type(None)),
            'fecha_ultimo_analisis': (datetime, type(None))
        }
    },
    'player_strokes': {
        'fields': {
            'user_id': str,
            'timestamp': (datetime, type(None)),
            'strokes': dict
        }
    },
    'padel_iq_history': {
        'fields': {
            'user_id': str,
            'timestamp': 'timestamp',
            'padel_iq': float,
            'tecnica': float,
            'ritmo': float,
            'fuerza': float,
            'tipo_analisis': str
        }
    },
    'video_analisis': {
        'fields': {
            'user_id': str,
            'video_url': str,
            'tipo_video': str,
            'fecha_analisis': 'timestamp',
            'estado': str,
            'resultados': dict,
            'preview_frames': list
        }
    }
}

def validate_document(collection_name, document_data):
    """Valida que un documento cumpla con el esquema definido."""
    if collection_name not in COLLECTIONS:
        raise ValueError(f"Colección {collection_name} no definida en el esquema")
        
    schema = COLLECTIONS[collection_name]['fields']
    for field, field_type in schema.items():
        if field not in document_data:
            raise ValueError(f"Campo requerido {field} no presente en el documento")
        if isinstance(field_type, tuple):
            if not any(isinstance(document_data[field], t) for t in field_type):
                raise ValueError(f"Tipo de dato incorrecto para {field}. Esperado: {field_type}, Recibido: {type(document_data[field])}")
        elif field_type == 'timestamp':
            if not isinstance(document_data[field], datetime):
                raise ValueError(f"Tipo de dato incorrecto para {field}. Esperado: datetime, Recibido: {type(document_data[field])}")
        else:
            if not isinstance(document_data[field], field_type):
                raise ValueError(f"Tipo de dato incorrecto para {field}. Esperado: {field_type}, Recibido: {type(document_data[field])}")
    
    return True 