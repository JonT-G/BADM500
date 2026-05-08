"""Generate Actor keypairs for any Profiles created before the keypair fields existed.

Lives in the federation app (rather than videos) so that the dependency direction
stays federation -> videos, matching the architecture.
"""

from django.db import migrations


def backfill_keypairs(apps, schema_editor):
    from federation.RSA import generate_actor_keypair

    Profile = apps.get_model('videos', 'Profile')
    for profile in Profile.objects.filter(public_key=''):
        private_pem, public_pem = generate_actor_keypair()
        Profile.objects.filter(pk=profile.pk).update(
            private_key=private_pem,
            public_key=public_pem,
        )


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('videos', '0005_profile_private_key_profile_public_key'),
    ]

    operations = [
        migrations.RunPython(backfill_keypairs, migrations.RunPython.noop),
    ]
