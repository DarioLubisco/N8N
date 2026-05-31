# 🌐 Cristmedical — Especificaciones de API REST

**Fuente:** Documentación Oficial Cristmedical (`FAR01159 (3).rar`)
**Código de Cliente:** `FAR01159`
**Protocolo:** HTTP REST API (No usa FTP)

---

## 🔌 Parámetros de Autenticación
Todas las peticiones a la API deben incluir los siguientes encabezados (Headers):

```http
Authorization: Bearer xiRcZ3LKR8PAg4Zd4U0ALzVvkVPNch3KSMA5igcXy6qRCZN3sVwjoAI5bnshjSyTAnSSlGh43u1YVHcW
Content-Type: application/json
```

---

## 📥 1. Inventario / Artículos (BAJADA)

**Endpoint:** `GET https://apienterprise.cristmedicals.com/api/v1/articulos`
**Query Parameters:**
- `co_cli` = `FAR01159`

### Estructura de Respuesta Exitosa (200 OK):
```json
{
  "co_cli": "FAR01159",
  "total_en_esta_pagina": 58,
  "articulos": [
    {
      "co_art": "AMP00100C",
      "des_art": "9 VIT INFUSION MULTIVITAMINICA AMP I.V (DPT) FV. 05/2027",
      "codigo_barra": "646824105066",
      "unidad": "UND",
      "precio_base": 17.44444,
      "porc_descuento": 0,
      "precio_con_descuento": 17.44,
      "stock_por_region": [
        {
          "co_alma": "01",
          "nombre": "Táchira",
          "disponible": 421
        }
      ]
    }
  ]
}
```
*Nota: Al momento de sincronizar el inventario, es importante iterar sobre `stock_por_region` para identificar el almacén o consolidar la disponibilidad total.*

---

## 📤 2. Pedidos (SUBIDA)

**Endpoint:** `POST https://apienterprise.cristmedicals.com/api/v1/pedidos`

### Estructura del JSON (Body):
```json
{
  "fact_num": 1001,
  "nombre":   "FARMACIA AMERICANA, C.A.",
  "rif":      "J-41074957-1",
  "co_cli":   "FAR01159",
  "co_ven":   "VEN01",
  "fec_emis": "2026-04-24",
  "fec_venc": "2026-05-24",
  "tasa":     36.50,
  "moneda":   "USD",
  "tot_bruto": 100.00,
  "tot_neto":  116.00,
  "iva":       16.00,
  "renglones": [
    {
      "reng_num":  1,
      "co_art":    "ART001",
      "co_alma":   "01",
      "total_art": 2,
      "prec_vta":  50.00,
      "reng_neto": 100.00
    }
  ]
}
```
*(Los parámetros de cliente pueden ser estáticos para nuestra instancia, y `renglones` debe generarse dinámicamente en formato array durante el sub-flujo de pedidos).*

---

## 📥 3. Facturas (BAJADA)

**Endpoint:** `POST https://apienterprise.cristmedicals.com/api/v1/facturas`

**Query Parameters:**
- `co_cli` = `FAR01159`
- `fec_desde` = `YYYY-MM-DD`
- `fec_hasta` = `YYYY-MM-DD`

### Estructura de Respuesta:
```json
{
  "factura_1": {
    "fact_num": "321503",
    "fec_emis": "2026-02-05",
    "cliente": "XXXXXXXXXX",
    "rif": "XXXXXXXXXXXX",
    "sub_total": 2338.88,
    "descuento": 327.44,
    "base16": 0.00,
    "iva16": 0.00,
    "exento": 2011.44,
    "total_bruto": 2338.88,
    "total_neto": 2011.44,
    "tasa": 378.4582,
    "articulos": {
      "renglon_1": {
        "sku": "021281892214",
        "descrip": "GLIBENCLAMIDA 5MG CJ X 30 TABL",
        "cant": 2,
        "precio": 1169.44,
        "desc_monto": 0.00,
        "neto_und": 1169.44,
        "total": 2338.88
      }
    },
    "fin_factura": true
  }
}
```
