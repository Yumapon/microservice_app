<#import "template.ftl" as layout>
<#assign kcPageTitle = msg("appname")>
<@layout.registrationLayout displayInfo=false; section>

<#if section == "header">

<#elseif section == "form">

<div class="app-logo">
    <img src="${url.resourcesPath}/img/logo.png" alt="Insurance App Logo">
</div>

<div class="login-wrapper">
    <div class="login-card">
        <div class="form-title">${msg("registerTitle")}</div>
        <form id="kc-register-form" onsubmit="register.disabled=true; return true;" action="${url.registrationAction}" method="post">
            <div class="form-group">
                <label for="firstname">${msg("firstname")}</label>
                <input type="text" id="firstname" name="firstName" value="${register.formData.firstName!}">
            </div>
            <div class="form-group">
                <label for="lastname">${msg("lastname")}</label>
                <input type="text" id="lastname" name="lastName" value="${register.formData.lastName!}">
            </div>
            <div class="form-group">
                <label for="email">${msg("email")}</label>
                <input type="email" id="email" name="email" value="${register.formData.email!}">
            </div>
            <div class="form-group">
                <label for="username">${msg("username")}</label>
                <input type="text" id="username" name="username" autofocus value="${register.formData.username!}">
            </div>
            <div class="form-group">
                <label for="password">${msg("password")}</label>
                <input type="password" id="password" name="password">
            </div>
            <div class="form-group">
                <label for="password-confirm">${msg("passwordConfirm")}</label>
                <input type="password" id="password-confirm" name="password-confirm">
            </div>
            <button type="submit">${msg("register")}</button>
        </form>
        <div class="links">
            <a href="${url.loginUrl}">${msg("backToLogin")}</a>
        </div>
    </div>
</div>

<#elseif section == "info">

</#if>

</@layout.registrationLayout>
