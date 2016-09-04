from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from django_lti_login.models import LTIClient

class Command(BaseCommand):
    help = 'Adds new lti login key and generates secret for it'

    def add_arguments(self, parser):
        parser.add_argument('-k', '--key',
                            help="Key identifier. Only alphanumerals are allowed. Default: generate new")
        parser.add_argument('-s', '--secret',
                            help="Key secret. Only alphanumerals are allowed. Default: generate new")
        parser.add_argument('-d', '--desc',
                            required=True,
                            help="Description for this key")

    def handle(self, *args, **options):
        key = options['key']
        secret = options['secret']
        desc = options['desc']

        lticlient = None
        while not lticlient:
            # create new
            lticlient = LTIClient()
            if key:
                lticlient.key = key
            if secret:
                lticlient.secret = secret
            lticlient.description = desc

            # validate it
            try:
                lticlient.full_clean()
                self.stdout.write(self.style.ERROR("WTF. full_clean ok"))
            except ValidationError as e:
                lticlient = None
                if key:
                    for field, errors in e.message_dict.items():
                        self.stdout.write(self.style.ERROR("Errors in field {!r}:".format(field)))
                        for error in errors:
                            self.stdout.write(self.style.ERROR("  {}".format(error)))
                    raise CommandError("Given data was invalid. Check above errors.")
           
            # save it
            if lticlient:
                lticlient.save()

        self.stdout.write(self.style.SUCCESS("Successfully created new lti login key and secret"))

        self.stdout.write(
            "   key: {c.key}\n"
            "secret: {c.secret}\n"
            "  desc: {c.description}"
            .format(c=lticlient)
        )
