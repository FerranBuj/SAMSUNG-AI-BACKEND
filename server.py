from pathlib import Path
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any
from PIL import Image
import io
import os
import json
from database import Database

app = FastAPI()
db = Database()

class User(BaseModel):
    nombre: str
    apellido: str
    rut: str
    telefono: str

class Avistamiento(BaseModel):
    confirmado_autoridades: bool
    ubicacion: Dict[str, Any]
    fecha: str
    adulto: bool
    usuario_id: int

class ImageResponse(BaseModel):
    archivo: str
    miniatura: str

class CaseResponse(BaseModel):
    fecha: str
    ubicacion: Dict[str, Any]
    confirmado_autoridades: bool
    imagenes: List[ImageResponse]

@app.post("/almacenar_usuario/")
async def almacenar_usuario(user: User):
    try:
        db.insert_user(user.nombre, user.apellido, user.rut, user.telefono)
        return {"message": "Usuario almacenado correctamente."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/almacenar_imagen/")
async def almacenar_imagen(
    confirmado_autoridades: bool = Form(...),
    latitud: float = Form(...),
    longitud: float = Form(...),
    fecha: str = Form(...),
    adulto: bool = Form(...),
    usuario_id: int = Form(...),
    archivo: UploadFile = File(...),
):
    try:
        ubicacion = {"latitud": latitud, "longitud": longitud}
        db.insert_avistamiento(confirmado_autoridades, ubicacion, fecha, adulto, usuario_id)
        avistamiento_id = db.conn.execute('SELECT last_insert_rowid()').fetchone()[0]

        # Process the image
        image_data = await archivo.read()
        image = Image.open(io.BytesIO(image_data))
        
        # Save original image
        original_path = f"images/{archivo.filename}"
        image.save(original_path)

        # Create and save thumbnail
        thumbnail = image.copy()
        thumbnail.thumbnail((128, 128))
        thumbnail_path = f"thumbnails/{archivo.filename}"
        thumbnail.save(thumbnail_path)

        # Insert image record
        db.insert_imagen(original_path, thumbnail_path, avistamiento_id)

        return {"message": "Imagen y avistamiento almacenados correctamente."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/casos/", response_model=List[CaseResponse])
async def casos():
    try:
        avistamientos = db.conn.execute('SELECT * FROM Avistamiento').fetchall()
        response = []

        for avistamiento in avistamientos:
            avistamiento_id, confirmado_autoridades, ubicacion, fecha, adulto, usuario_id = avistamiento
            ubicacion = json.loads(ubicacion)
            imagenes = db.conn.execute('SELECT archivo, miniatura FROM Imagen WHERE avistamiento_id = ?', (avistamiento_id,)).fetchall()
            
            imagenes_response = [ImageResponse(archivo=img[0], miniatura=img[1]) for img in imagenes]

            response.append(CaseResponse(
                fecha=fecha,
                ubicacion=ubicacion,
                confirmado_autoridades=confirmado_autoridades,
                imagenes=imagenes_response
            ))

        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    os.makedirs("images", exist_ok=True)
    os.makedirs("thumbnails", exist_ok=True)
    uvicorn.run(app, host="127.0.0.1", port=8007)
    print("Running Uvicorn at 8007")
