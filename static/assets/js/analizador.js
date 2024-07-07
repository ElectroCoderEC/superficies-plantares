/*=============================================
			AL INICIAR LA PAGINA
=============================================*/
$(document).ready(function () {

	function updateValue(inputId, labelId) {
		$('#' + labelId).text($('#' + inputId).val());
		$('#' + inputId).on('input', function () {
			$('#' + labelId).text($(this).val());

			$.ajax({
				url: '/set_controles',
				method: 'POST',
				contentType: 'application/json',
				data: JSON.stringify({ "control": inputId, "valor": $('#' + inputId).val() }),
				success: function (response) {
					// Puedes manejar la respuesta si es necesario
					console.log(response.message);
				}
			});

		});

	}


	function defaultValue(inputId) {

		$.ajax({
			url: '/set_controles',
			method: 'POST',
			contentType: 'application/json',
			data: JSON.stringify({ "control": inputId, "valor": $('#' + inputId).val() }),
			success: function (response) {
				// Puedes manejar la respuesta si es necesario
				console.log(response.message);
			}
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

	$('#btnDefault').click(function () {

		$('#lower-h').val(30)
		$('#lower-s').val(16)
		$('#lower-v').val(103)

		$('#upper-h').val(94)
		$('#upper-s').val(255)
		$('#upper-v').val(255)

		$('#lower-h-dedos').val(40)
		$('#lower-s-dedos').val(16)
		$('#lower-v-dedos').val(87)

		$('#upper-h-dedos').val(100)
		$('#upper-s-dedos').val(255)
		$('#upper-v-dedos').val(255)

		defaultValue("lower-h")
		defaultValue("lower-s")
		defaultValue("lower-v")
		defaultValue("upper-h")
		defaultValue("upper-s")
		defaultValue("upper-v")

		defaultValue("lower-h-dedos")
		defaultValue("lower-s-dedos")
		defaultValue("lower-v-dedos")
		defaultValue("upper-h-dedos")
		defaultValue("upper-s-dedos")
		defaultValue("upper-v-dedos")




	});



});


$('.tipoVideo').on('change', function () {
	console.log(this.value);
	const selectedValue = this.value;

	if (selectedValue == "normal") {
		$('#contenedorControles').hide();
		$('#contenedorPies').hide();
		$('#contenedorBotones').hide();
	}

	else {
		$('#contenedorControles').show();
		$('#contenedorPies').show();
		$('#contenedorBotones').show();
	}

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