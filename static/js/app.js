$(document).ready(function () {

    // Apaga mensagens de alerta
    if ($('.message-alert').length > 0) {
        setTimeout(function () {
            $('.message-alert').fadeOut('slow');
        }, 3000);
    };
});

// Copia texto para área de transferência - função global
function copyToClipboard(button) {
    const text = button.getAttribute('data-text');
    navigator.clipboard.writeText(text).then(function () {
        // Opcional: mostrar uma notificação de sucesso
        console.log('Texto copiado para a área de transferência');
    }).catch(function (err) {
        console.error('Erro ao copiar texto: ', err);
    });
}