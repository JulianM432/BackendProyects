from pydantic import BaseModel, Field

class CanchaModel(BaseModel):
    nombre: str = Field(..., min_length=3, description="Nombre de la cancha")
    techada: bool = Field(False, description="Si la cancha es techada")
    class Config:
        from_atributes = True


# class CanchaModelOut(CanchaModel):
#     id: int
