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
        <div class="form-title">${msg("updatePasswordTitle")}</div>
        <form id="kc-update-password-form" onsubmit="update.disabled=true; return true;" action="${url.loginAction}" method="post">
            <div class="form-group">
                <label for="password-new">${msg("newPassword")}</label>
                <input type="password" id="password-new" name="password-new" autofocus>
            </div>
            <div class="form-group">
                <label for="password-confirm">${msg("passwordConfirm")}</label>
                <input type="password" id="password-confirm" name="password-confirm">
            </div>
            <button type="submit">${msg("updatePassword")}</button>
        </form>
        <div class="links">
            <a href="${url.loginUrl}">${msg("backToLogin")}</a>
        </div>
    </div>
</div>

<#elseif section == "info">

</#if>

</@layout.registrationLayout>
