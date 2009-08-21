from helixcore.validol.validol import validate, AnyOf, Scheme


BUGGY = {
    'client_id': AnyOf(str, unicode),
    'product_id': AnyOf(str, unicode),
}

result = validate(
    Scheme(BUGGY),
    {
        'client_id': 'id',
        'product_id': 'super-light 555',
    }
)

print result