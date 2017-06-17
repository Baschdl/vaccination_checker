if (window.File && window.FileReader && window.FormData) {
	var $inputField = $('#file');

	$inputField.on('change', function (e) {
		var file = e.target.files[0];

		if (file) {
			if (/^image\//i.test(file.type)) {
				readFile(file);
			} else {
				alert('Not a valid image!');
			}
		}
	});
} else {
	alert("File upload is not supported!");
}

function readFile(file) {
	var reader = new FileReader();

	reader.onloadend = function () {
		processFile(reader.result, file.type);
	}

	reader.onerror = function () {
		alert('There was an error reading the file!');
	}

	reader.readAsDataURL(file);
	sendFile(reader)
}

function sendFile(fileData) {
	var formData = new FormData();

	formData.append('imageData', fileData);

	$.ajax({
		type: 'POST',
		url: '/your/upload/url',
		data: formData,
		contentType: false,
		processData: false,
		success: function (data) {
			if (data.success) {
				alert('Your file was successfully uploaded!');
			} else {
				alert('There was an error uploading your file!');
			}
		},
		error: function (data) {
			alert('There was an error uploading your file!');
		}
	});
}