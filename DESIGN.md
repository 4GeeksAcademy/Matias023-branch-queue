# Branch Queue — Design Notes

## Estructura de datos

BranchQueue mantiene una cola independiente por cada tipo de servicio utilizando `collections.deque`.

Los tipos de servicio son:

 - `deposito`
 - `retiro`
 - `gestion_cuenta`

Cada cola preserva FIFO de forma natural. El contador de tickets es global y compartido entre todas las colas, por lo que los números son secuenciales independientemente del servicio.

## Por qué colas separadas

Una cola separada por tipo de servicio permite que `call_next(service_type)` y `peek_next(service_type)` accedan directamente a la cola correcta sin recorrer clientes de otros servicios.

Con una sola lista compartida, cada agente tendréa que buscar el siguiente cliente de su tipo, haciendo la operación mens eficiente a medida que la sala se llena.

## Concurrencia

Este proyecto es un CLI de un solo proceso y nü implementa concurrencia real.

En producción, si dos agentes del mismo tipo de servicio ejecutaran `call_next` al mismo tiempo, la operación de retirar el ticket de la cola debería ser atïmica.

El orden correcto sería:

1. Adquirir un lock o iniciar una transacción.
2. Seleccionar el primer ticket de la cola.
3. Retirar el ticket de la cola y marcarlo como en procesamiento dentro de la misma operación atómica.
4. Confirmar el cambio.
5. Liberar el lock o cerrar la transacción.

Así el segundo agente ya no puede ver ni retirar el mismo ticket.
