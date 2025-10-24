from .models import Category

def base_context(request):
    """
    Add categories to all templates context
    """
    return {
        'categories': Category.objects.all(),
    }
