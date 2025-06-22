<#import "template.ftl" as layout>
<#assign kcPageTitle = msg("verifyEmailTitle")>
<@layout.registrationLayout displayInfo=false; section>

<#if section == "header">

<#elseif section == "form">

<div class="app-logo">
    <img src="${url.resourcesPath}/img/logo.png" alt="Insurance App Logo">
</div>

<div class="login-wrapper">
    <div class="login-card">
        <div class="form-title">${msg("verifyEmailTitle")}</div>
        <div class="form-group">
            <p>${msg("verifyEmailText")}</p>
        </div>
        <div class="links">
            <a href="${url.loginUrl}">${msg("backToLogin")}</a>
        </div>
    </div>
</div>

<#elseif section == "info">

</#if>

</@layout.registrationLayout>
