var fields = new Set(["csrf_token", "unit_id", "submit"]);
function addFormField() {
    var field = prompt("请输入指标名：");
    if (!field) { alert("指标名不能为空！"); return; }
    if (fields.has(field)) { alert("指标名已存在或不合法！"); return; }
    fields.add(field);
    var form = document.getElementsByClassName("form")[0];
    console.log(form);
    var submit = form.getElementsByClassName("btn btn-default")[0];
    var div = document.createElement("div");
    div.setAttribute("class", "form-group ");
    var label = document.createElement("label");
    label.setAttribute("class", "control-label");
    label.setAttribute("for", field);
    label.innerText = field;
    div.appendChild(label);
    var input = document.createElement("input");
    input.setAttribute("class", "form-control");
    input.setAttribute("id", field);
    input.setAttribute("name", field);
    input.setAttribute("type", "text");
    input.setAttribute("value", "");
    input.setAttribute("required", "required");
    div.appendChild(input);
    form.insertBefore(div, submit)
}