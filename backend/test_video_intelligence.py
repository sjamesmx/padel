from google.cloud import videointelligence_v1

try:
    client = videointelligence_v1.VideoIntelligenceServiceClient()
    print("Video Intelligence inicializado correctamente")
except Exception as e:
    print(f"Error: {str(e)}")