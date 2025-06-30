<#import "template.ftl" as layout>
<#assign kcPageTitle = msg("appname") + " - " + msg("signin")>
<@layout.registrationLayout displayInfo=false; section>

<#if section == "header">

<#elseif section == "form">

<div class="app-logo">
    <img src="${url.resourcesPath}/img/logo.png" alt="Insurance App Logo">
</div>

<div class="login-wrapper">
    <div class="login-card">
        <div class="form-title">${msg("hellomsg")}</div>

        <form id="kc-form-login" onsubmit="login.disabled=true; return true;" action="${url.loginAction}" method="post">
            <div class="form-group">
                <label for="username">${msg("username")}</label>
                <input type="text" id="username" name="username" autofocus value="${username!}">
            </div>

            <div class="form-group">
                <label for="password">${msg("password")}</label>
                <div class="password-wrapper">
                    <input type="password" id="password" name="password">
                </div>
            </div>
            
            <button type="submit">${msg("signin")}</button>
        </form>

        <div class="links">
            <#if realm.resetPasswordAllowed>
                <a href="${url.loginResetCredentialsUrl}">${msg("forgotPassword")}</a>
            </#if>
        </div>
    </div>
</div>

<div class="register">
    <#if realm.registrationAllowed>
        <span>${msg("signupmsg")}</span>
        <a class="signup-link" href="${url.registrationUrl}">${msg("signup")}</a>
    </#if>
</div>

<#elseif section == "info">

</#if>

</@layout.registrationLayout>