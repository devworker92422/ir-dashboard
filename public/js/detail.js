$('#submitBtn').click(function () {
    let feedback = $('#feedbackMsg').val();
    let payload = {
        feedback
    }
    $.ajax({
        url: '/api/feedback',
        method: 'POST',
        data: payload,
        success: function (res) {
            console.log(res);
        }
    })
})