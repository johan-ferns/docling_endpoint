# Docling endpoint experiment


- Models:

    TODO : Provide details on how the models are stored here. (Tabletransformer and Layout Heron model)

- Accessing on the zone:
    - start server: 

        uvicorn src.docling_endpoint.api:app --reload

    - on another terminal send the file:

        curl -X POST "http://127.0.0.1:8000/upload/extract?output_format=markdown"   -H "accept: application/json"   -H "Content-Type: multipart/form-data"   -F "file=@ABSOLUTE PATH TO FILE/Latest AI Advancements.pdf"
