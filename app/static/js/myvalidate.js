function validate_required(field,alerttxt)
{
with (field)
  {
  if (value==null||value=="")
    {alert(alerttxt);return false}
  else {return true}
  }
}

function validate_password_length(password,alerttxt)
{
with (password)
  {
    if (value.length < 6)
      {alert(alerttxt); return false}
    else
      {return true}
  }
}

function validate_passwords_equal(password1, password2, alerttxt)
{
  if (password1.value != password2.value)
    {alert(alerttxt); return false}
  else
    {return true}
}



function validate_form_reset(thisform)
{
with (thisform)
  {
  if (validate_required(password_old,"请输入原密码")==false)
    {password_old.focus();return false}
   
  if (validate_required(password_new_1,"请输入新密码")==false)
    {password_new_1.focus();return false}
   
  if (validate_required(password_new_2,"请输入新密码")==false)
    {password_new_2.focus();return false}

  if (validate_password_length(password_old, "原密码长度需要大于等于6")==false)
    {password_old.focus(); return false}
  if (validate_password_length(password_new_1, "新密码长度需要大于等于6")==false)
    {password_new_1.focus(); return false}
  if (validate_password_length(password_new_2, "新密码长度需要大于等于6")==false)
    {password_new_2.focus(); return false}

  if (validate_passwords_equal(password_new_1, password_new_2, "两次输入新密码不同")==false)
    {password_new_1.focus(); return false}
  }
}

