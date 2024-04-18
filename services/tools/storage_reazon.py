def getStorageReazons(end: bool = False) -> list[list[str]]:
    reazons = []

    if not end:
        reazons.append(("capacity", "Falta de capacidad en el taller"))
        reazons.append(("approval", "Pendiente por aprobación del cliente"))

    reazons.append(("ready", "Listo para recoger"))
    reazons.append(("storage_service", "Servicio de storage"))

    return reazons
