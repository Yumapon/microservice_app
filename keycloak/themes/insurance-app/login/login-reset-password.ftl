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
        <div class="form-title">${msg("resetTitle")}</div>
        <form id="kc-reset-password-form" onsubmit="reset.disabled=true; return true;" action="${url.loginAction}" method="post">
            <div class="form-group">
                <label for="username">${msg("usernameOrEmail")}</label>
                <input type="text" id="username" name="username" autofocus value="${username!}">
            </div>
            <button type="submit">${msg("sendReset")}</button>
        </form>
        <div class="links">
            <a href="${url.loginUrl}">${msg("backToLogin")}</a>
        </div>
    </div>
</div>

<#elseif section == "info">

</#if>

</@layout.registrationLayout>
