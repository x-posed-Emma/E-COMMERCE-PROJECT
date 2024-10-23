def vendor_status(request):
    """Returns whether the user is a vendor."""
    if request.user.is_authenticated:
        return {'is_vendor': hasattr(request.user, 'vendor_profile')}
    return {'is_vendor': False}