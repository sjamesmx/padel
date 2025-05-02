from firebase_admin import firestore, initialize_app
import firebase_admin

# Inicializar Firebase
initialize_app()

def clean_strokes(user_id):
    db = firestore.client()
    user_ref = db.collection('users').document(user_id)
    doc = user_ref.get()
    if not doc.exists:
        print("Documento no existe")
        return

    data = doc.to_dict()
    strokes = data.get('strokes', [])
    # Filtrar entradas no deseadas
    cleaned_strokes = [stroke for stroke in strokes if stroke['video_url'] != "https://example.com/video.mp4"]
    # Opcional: Filtrar duplicados basados en video_url
    seen_urls = set()
    unique_strokes = []
    for stroke in cleaned_strokes:
        if stroke['video_url'] not in seen_urls:
            unique_strokes.append(stroke)
            seen_urls.add(stroke['video_url'])

    # Actualizar Firestore
    user_ref.update({'strokes': unique_strokes})
    print("Firestore actualizado")

if __name__ == "__main__":
    clean_strokes("nTnLmtl90Ud0Zpcj1L5fv34nZYv1")