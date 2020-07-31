function clickClienteL()
{
console.log()
    if(document.getElementById("cnpj_cliente").value =='')
    {
        alert("Preencher CNPJ do Cliente!");
    }
    if(document.getElementById("contact_cliente").value =='')
    {
        alert("Preencher Contato do Cliente!!");
    }

     document.getElementById('nav-home-tab').classList.remove("active");
     document.getElementById('nav-contact-tab1').classList.add("active");
     document.getElementById('nav-contact-tab').classList.remove("active");
}

function clickInfoR()
{
     document.getElementById('nav-home-1').classList.remove("active");
     document.getElementById('nav-home-tab').classList.add("active");
     document.getElementById('nav-contact-tab-1').classList.remove("active");
}

function consultaCNPJRV()
{
    var json = consultaCNPJ2();
    json.then(function(value) {
        if(value.situacao != "ATIVA")
        {
            alert("CNPJ não está com situação ativa!");
        }
        document.getElementById('razao_revenda').value = value.fantasia;
        document.getElementById('state_revenda').value = value.uf;
        document.getElementById('cep_revenda').value = value.cep;
        document.getElementById('address_revenda').value = value.logradouro;
        document.getElementById('city_revenda').value = value.municipio;
        document.getElementById('phone_revenda').value = value.telefone;
        document.getElementById('email_revenda').value = value.email;
        if(document.getElementById('situacao_revenda'))
        {
            document.getElementById('email_revenda').value = value.situacao;
        }
}, function(value) {
  //
});
}

function consultaCNPJ()
{
    var json = consultaCNPJ2();
    json.then(function(value) {
        if(value.situacao != "ATIVA")
        {
            alert("CNPJ não está com situação ativa!");
        }
        document.getElementById('razao_cliente').value = value.fantasia;
        document.getElementById('state_cliente').value = value.uf;
        document.getElementById('cep_cliente').value = value.cep;
        document.getElementById('address_cliente').value = value.logradouro;
        document.getElementById('city_cliente').value = value.municipio;
        document.getElementById('phone_cliente').value = value.telefone;
        document.getElementById('email_cliente').value = value.email;
}, function(value) {
  //
});
}

function consultaCNPJ2() {
    var cnpj = document.getElementById('cnpj_cliente').value;
    cnpj = cnpj.replace(/\D/g, '');

    return jsonp('https://www.receitaws.com.br/v1/cnpj/' + encodeURI(cnpj), 60000)
        .then((json) => {
            if (json['status'] === 'ERROR') {
                return Promise.reject(json['message']);
            } else {
                return Promise.resolve(json);
            }
        });
}

function clickC()
{
    document.getElementById('nav-profile-tab1').classList.remove("active");
    document.getElementById('nav-contact-tab1').classList.add("active");
    document.getElementById('nav-contact-tab2').classList.remove("active");
}

function clickEquip()
{
    document.getElementById('nav-about-tab').classList.remove("active");
    document.getElementById('nav-about-vendedor-tab').classList.add("active");
    document.getElementById('nav-about-vendedor-tab1').classList.remove("active");
}

function clickCliente()
{
    document.getElementById('nav-home-tab').classList.remove("active");
    document.getElementById('nav-profile-tab1').classList.add("active");
    document.getElementById('nav-contact-tab').classList.remove("active");
}

function clickInfo()
{
    document.getElementById('nav-contact-tab1').classList.remove("active");
    document.getElementById('nav-about-tab').classList.add("active");
    document.getElementById('nav-about-tab1').classList.remove("active");
}

function add()
{
    var tb1 = document.createElement("tr");
	document.getElementById("tbpn").appendChild(tb1);
	var row = document.getElementsByTagName('tr');
	var length = row.length - 4;
	console.log(length)
	tb1.innerHTML+= '<td><input type="text" name="pn_projeto'+length+'" id="pn_projeto'+length+'" class="form-control shadow-none my-1"></td>';
	tb1.innerHTML+='<td><input type="text" name="desc_projeto'+length+'" id="desc_projeto'+length+'" class="form-control shadow-none my-1"></td>';
	tb1.innerHTML+='<td><input type="text" name="qty_projeto'+length+'" id="qty_projeto'+length+'" class="form-control shadow-none my-1"></td>';
	tb1.innerHTML+='<td><input type="text" name="value_projeto'+length+'" id="value_projeto'+length+'" class="form-control shadow-none my-1"></td>';
    tb1.innerHTML+='<td><a style="color: white;" id="btn_pn'+length+'" class="btn btn-danger" onclick="rm_pn('+length+')">X</a></td>';
}

function rm_pn(num)
{
    var c1 = document.getElementById("pn_projeto"+num);
    c1.parentNode.removeChild(c1);
    var c2 = document.getElementById("desc_projeto"+num);
    c2.parentNode.removeChild(c2);
    var c3 = document.getElementById("qty_projeto"+num);
    c3.parentNode.removeChild(c3);
    var c4 = document.getElementById("value_projeto"+num);
    c4.parentNode.removeChild(c4);
    var c5 = document.getElementById("btn_pn"+num);
    c5.parentNode.removeChild(c5);
}

function rm_ac(num)
{
    var c1 = document.getElementById("ac_pn_projeto"+num);
    c1.parentNode.removeChild(c1);
    var c2 = document.getElementById("ac_desc_projeto"+num);
    c2.parentNode.removeChild(c2);
    var c3 = document.getElementById("ac_qty_projeto"+num);
    c3.parentNode.removeChild(c3);
    var c4 = document.getElementById("ac_value_projeto"+num);
    c4.parentNode.removeChild(c4);
    var c5 = document.getElementById("ac_btn_pn"+num);
    c5.parentNode.removeChild(c5);
}

function add_ac()
{
    var tb1 = document.createElement("tr");
	document.getElementById("tbac").appendChild(tb1);
	var row = document.getElementsByTagName('tr');
	var length2 = row.length - 5;
	console.log(length2)
	tb1.innerHTML+= '<td><input type="text" name="ac_pn_projeto'+length2+'" id="ac_pn_projeto'+length2+'" class="form-control shadow-none my-1"></td>';
	tb1.innerHTML+='<td><input type="text" name="ac_desc_projeto'+length2+'" id="ac_desc_projeto'+length2+'" class="form-control shadow-none my-1"></td>';
	tb1.innerHTML+='<td><input type="text" name="ac_qty_projeto'+length2+'" id="ac_qty_projeto'+length2+'" class="form-control shadow-none my-1"></td>';
	tb1.innerHTML+='<td><input type="text" name="ac_value_projeto'+length2+'" id="ac_value_projeto'+length2+'" class="form-control shadow-none my-1"></td>';
	tb1.innerHTML+='<td><a style="color: white;" id="ac_btn_pn'+length2+'" class="btn btn-danger" onclick="rm_ac('+length2+')">X</a></td>';

}