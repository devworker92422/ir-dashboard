$(document).ready(function () {

  var collaps = $('[id*="collapse"]');
  for (var i = 0; i < collaps.length; i++) {
    var id = collaps.eq(i).attr('id').replace('collapse', '');
    var quill = new Quill("#editor" + id, {
      theme: "snow",
    });
    var answer = $("#answer" + id).val()
    if (answer) {
      quill.root.innerHTML = answer
    }
  }
  var quills = document.querySelectorAll('[id*="editor"]');
  quills.forEach(function (quill) {
    var q = Quill.find(quill);
    q.on('text-change', function (delta, oldDelta, source) {
      var faq_id = q.container.id.replace('editor', '');
      console.log(faq_id);
      $("#answer" + faq_id).val(q.root.innerHTML);
    });
  });
});
