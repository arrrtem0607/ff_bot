class Validator:
    @staticmethod
    def num_check(number: str) -> bool:
        try:
            int(number)
            return True
        except ValueError:
            return False
