
const make_request = async (metodo, datos, url, responseType = 'json') => {

    try {
        const response = await axios({
            method: metodo,
            url: url,
            data: datos,
            responseType: responseType,
        });
        return response.data;
    } catch (error) {
        console.error("Error in requisition:", error);
        throw error;
    }
};

const mensaje_success = (title, mensaje) => {
    Swal.fire({
        position: "top-end",
        icon: "success",
        title: title,
        text: mensaje,
        showConfirmButton: false,
        timer: 5000,
    });
};

const mensaje_error = (title, mensaje) => {
    Swal.fire({
        position: "top-end",
        icon: "error",
        title: title,
        text: mensaje,
        showConfirmButton: false,
        timer: 4000,
    });
};


const get_data_by_region = async () => {
    const get_data_button = document.getElementById("get_data_button");
    const region_input = document.getElementById("region_input");
    const loading = document.getElementById("loading");

    if (region_input.value === "") {
        mensaje_error("Error", "Você precisa incluir uma região para usar o crawler");
        get_data_button.hidden = false;
        return;
    }

    get_data_button.hidden = true;
    loading.hidden = false;
    region_input.disabled = true;

    mensaje_success("",
        `O crawler está coletando os dados. 
        Por favor, não atualize a página, pois o processo pode levar alguns minutos.`
    );

    try {
        response = await make_request("GET", {}, `/get_data/${region_input.value}`, "blob");
        const filename = `${region_input.value}.csv`
        const url = window.URL.createObjectURL(response);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);

        get_data_button.hidden = false;
        loading.hidden = true;
        region_input.disabled = false;
        region_input.value = "";
        mensaje_success("", `O processo foi finalizado. Os dados coletados já estão disponíveis em ${filename}`);


    } catch (error) {
        mensaje_error(
            "Error",
            "Não foi possível obter dados, tente novamente, verifique se é uma região válida");
        get_data_button.hidden = false;
        loading.hidden = true;
        region_input.disabled = false;        
        console.error(error);
        
    }


}

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("get_data_button").addEventListener("click", () => {
        get_data_by_region();
    });
    document.getElementById("get_data_button").addEventListener("keydown", (event) => {
        if (event.key === 'Enter') {
            get_data_by_region();
        }
    });
})


