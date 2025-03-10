from .assets import Animal
from fastapi import FastAPI, HTTPException
from fastapi.routing import APIRoute


def custom_generate_unique_id(route: APIRoute):
    return f"{route.tags[0]}-{route.name}"


app = FastAPI(title="Farmbase", generate_unique_id_function=custom_generate_unique_id)


data_store = {
    "Animal": [],
}

@app.post("/animal/", tags=["animals"])
def create_animal(animal: Animal):
    data_store["Animal"].append(animal)
    return {"message": "Animal created", "animal": animal}

@app.get("/animal/", tags=["animals"])
def list_animals():
    return data_store["Animal"]

@app.put("/animal/{index}", tags=["animals"])
def update_animal(index: int, animal: Animal):
    if index < 0 or index >= len(data_store["Animal"]):
        raise HTTPException(status_code=404, detail="Animal not found")
    data_store["Animal"][index] = animal
    return {"message": "Animal updated", "animal": animal}
