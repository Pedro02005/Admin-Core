document.addEventListener("DOMContentLoaded", function () {
    const complejo = document.getElementById("id_complejo");
    const cancha = document.getElementById("id_cancha");

    if (!complejo || !cancha) {
        return;
    }

    let solicitudActual;

    complejo.addEventListener("change", async function () {
        const complejoId = complejo.value;
        solicitudActual?.abort();
        cancha.replaceChildren(new Option("Seleccione una cancha", ""));
        cancha.disabled = Boolean(complejoId);

        if (!complejoId) {
            return;
        }

        const solicitud = new AbortController();
        solicitudActual = solicitud;
        const url = new URL(complejo.dataset.canchasUrl, document.baseURI);
        url.searchParams.set("complejo_id", complejoId);

        try {
            const respuesta = await fetch(url, { signal: solicitud.signal });
            if (!respuesta.ok) {
                throw new Error("No se pudieron cargar las canchas");
            }

            const datos = await respuesta.json();
            if (solicitud.signal.aborted) {
                return;
            }

            for (const item of datos.canchas) {
                cancha.add(new Option(item.nombre, item.id));
            }
        } catch (error) {
            if (!solicitud.signal.aborted) {
                alert("Ocurrió un error al cargar las canchas.");
                console.error(error);
            }
        } finally {
            if (!solicitud.signal.aborted) {
                cancha.disabled = false;
            }
        }
    });
});
