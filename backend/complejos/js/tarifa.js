document.addEventListener("DOMContentLoaded", function () {

    const complejo = document.getElementById("id_complejo");
    const cancha = document.getElementById("id_cancha");

    if (!complejo || !cancha) {
        return;
    }

    complejo.addEventListener("change", async function () {

        const complejoId = complejo.value;

        cancha.innerHTML = "";
        cancha.add(new Option("Seleccione una cancha", ""));

        if (!complejoId) {
            return;
        }

        cancha.disabled = true;

        const url = (
            "/admin/complejos/tarifa/canchas-por-complejo/"
            + "?complejo_id=" + encodeURIComponent(complejoId)
        );

        try {
            const respuesta = await fetch(url);

            if (!respuesta.ok) {
                throw new Error("No se pudieron cargar las canchas");
            }

            const datos = await respuesta.json();

            datos.canchas.forEach(function (item) {

                const opcion = new Option(
                    item.nombre,
                    item.id
                );

                cancha.add(opcion);
            });

        } catch (error) {
            alert("Ocurrió un error al cargar las canchas.");
            console.error(error);

        } finally {
            cancha.disabled = false;
        }

    });

});