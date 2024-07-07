/*=============================================
			AL INICIAR LA PAGINA
=============================================*/
$(document).ready(function () {


	function updateValue(inputId, labelId) {
		$('#' + labelId).text($('#' + inputId).val());
		$('#' + inputId).on('input', function () {
			$('#' + labelId).text($(this).val());
		});
	}

	updateValue('lower-h', 'lower-h-val');
	updateValue('lower-s', 'lower-s-val');
	updateValue('lower-v', 'lower-v-val');
	updateValue('upper-h', 'upper-h-val');
	updateValue('upper-s', 'upper-s-val');
	updateValue('upper-v', 'upper-v-val');

	updateValue('lower-h-dedos', 'lower-h-dedos-val');
	updateValue('lower-s-dedos', 'lower-s-dedos-val');
	updateValue('lower-v-dedos', 'lower-v-dedos-val');
	updateValue('upper-h-dedos', 'upper-h-dedos-val');
	updateValue('upper-s-dedos', 'upper-s-dedos-val');
	updateValue('upper-v-dedos', 'upper-v-dedos-val');



});


$('.tipoVideo').on('change', function () {
	console.log(this.value);
	const selectedValue = this.value;

	$.ajax({
		url: '/set_mode',
		method: 'POST',
		contentType: 'application/json',
		data: JSON.stringify({ mode: selectedValue }),
		success: function (response) {
			// Puedes manejar la respuesta si es necesario
			console.log(response.message);
		}
	});
});