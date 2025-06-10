from http import HTTPMethod

from django.forms import BaseForm
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render


def generic_create_view(
    request: HttpRequest,
    form: type[BaseForm],
    template_name: str = "object_form.html",
    redirect: str | None = None,
) -> HttpResponseRedirect | HttpResponse:
    if request.method == HTTPMethod.POST:
        form_obj = form(request.POST)
        if form_obj.is_valid():
            # some stuff
            if redirect is None:
                redirect = "/"
            return HttpResponseRedirect(redirect)

    return render(request, template_name, {"form": form()})
