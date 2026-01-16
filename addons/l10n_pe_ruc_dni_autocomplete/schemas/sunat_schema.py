from dataclasses import dataclass


@dataclass(frozen=True)
class SunatDTO:
    razon_social: str | None = None
    numero_documento: str | None = None
    estado: str | None = None
    condicion: str | None = None
    direccion: str | None = None
    ubigeo: str | None = None
    via_tipo: str | None = None
    via_nombre: str | None = None
    zona_codigo: str | None = None
    zona_tipo: str | None = None
    numero: str | None = None
    interior: str | None = None
    lote: str | None = None
    dpto: str | None = None
    manzana: str | None = None
    kilometro: str | None = None
    distrito: str | None = None
    provincia: str | None = None
    departamento: str | None = None
    es_agente_retencion: bool | None = None
    es_buen_contribuyente: bool | None = None
    locales_anexos: bool | None = None
    tipo: str | None = None
    actividad_economica: str | None = None
    numero_trabajadores: str | None = None
    tipo_facturacion: str | None = None
    tipo_contabilidad: str | None = None
    comercio_exterior: str | None = None

    @staticmethod
    def from_payload(payload: dict[str, str]):
        return SunatDTO(
            razon_social=payload.get('razon_social'),
            numero_documento=payload.get('numero_documento'),
            estado=payload.get('estado'),
            condicion=payload.get('condicion'),
            direccion=payload.get('direccion'),
            ubigeo=payload.get('ubigeo'),
            distrito=payload.get('distrito'),
            provincia=payload.get('provincia'),
            departamento=payload.get('departamento'),
            es_agente_retencion=payload.get('es_agente_retencion'),
            es_buen_contribuyente=payload.get('es_buen_contribuyente'),
            tipo=payload.get('tipo'),
            actividad_economica=payload.get('actividad_economica'),
            numero_trabajadores=payload.get('numero_trabajadores'),
            tipo_facturacion=payload.get('tipo_facturacion'),
            tipo_contabilidad=payload.get('tipo_contabilidad'),
            comercio_exterior=payload.get('comercio_exterior')
        )
