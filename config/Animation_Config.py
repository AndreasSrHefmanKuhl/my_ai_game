import os


class AnimationConfig:


    class Paths:
        """Enthält alle generischen Pfad- und Dateisystem-Konstanten."""

        # Basisverzeichnis des aktuellen Skripts
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    class Scarab:
        """
        Konfiguration und Eigenschaften, die spezifisch für das
        Scarab-Roboter-Objekt sind.
        """

        ASSET_PATH = os.path.normpath(
            os.path.join(AnimationConfig.Paths.BASE_DIR,
                "..",
                "assets",
                "Robot Warfare Asset Pack 22-11-24",
                "Robots",
                "Scarab.png",
            )
        )
        class Sprite_Stand:
            WIDTH=16
            HEIGHT=16
            Y_POS_ROW = 0

        class Sprite_Walk:
            WIDTH = 16
            HEIGHT = 16
            Y_POS_ROW = 16
            NUM_FRAMES = 4

        class Sprite_Shoot:
            WIDTH = 16
            HEIGHT = 16
            Y_POS_ROW =48
            NUM_FRAMES = 5


        class Properties:
            SCALE_FACTOR = 4
            MOVEMENT_SPEED_PIXELS_PER_SECOND = 60



    class Spider:
        """
        Konfiguration und Eigenschaften, die spezifisch für das
        Spider-Roboter-Objekt sind.
        """

        # Pfad zum Centipede.png Asset (Platzhalter für den tatsächlichen Dateinamen)
        ASSET_PATH = os.path.normpath(
            os.path.join(AnimationConfig.Paths.BASE_DIR,

                "..",
                "assets",
                "Robot Warfare Asset Pack 22-11-24",
                "Robots",
                "Spider.png",
            )
        )

        class Sprite_Walk:
            """Sprite-Definition und Animations-Konstanten für Spider."""

            WIDTH = 16
            HEIGHT = 16
            Y_POS_ROW = 16
            NUM_FRAMES = 4 #  4 Frames für eine fließendere Animation

        class Sprite_Shoot:
            WIDTH = 16
            HEIGHT = 16
            Y_POS_ROW = 48
            NUM_FRAMES = 5

        class Properties:
            """Rendering- und Bewegungseigenschaften für Spider."""

            SCALE_FACTOR = 4
            MOVEMENT_SPEED_PIXELS_PER_SECOND = 60  #


    class Wasp:

        ASSET_PATH = os.path.normpath(
            os.path.join(AnimationConfig.Paths.BASE_DIR,
                ".."
                "assets",
                "Robot Warfare Asset Pack 22-11-24",
                "Robots",
                "Wasp.png",
            )
        )

        class Sprite_Fly:


            WIDTH = 16
            HEIGHT = 16
            Y_POS_ROW = 0
            NUM_FRAMES = 8  #  8 Frames für eine fließendere Animation

        class Properties:

            SCALE_FACTOR = 2

    class Hornet:

        ASSET_PATH = os.path.normpath(
            os.path.join(AnimationConfig.Paths.BASE_DIR,
                         ".."
                         "assets",
                         "Robot Warfare Asset Pack 22-11-24",
                         "Robots",
                         "Hornet.png",
                         )
        )

        class Sprite_Fly:
            WIDTH = 16
            HEIGHT = 16
            Y_POS_ROW = 0
            NUM_FRAMES = 8  # 8 Frames für eine fließendere Animation

        class Sprite_Shoot:
            WIDTH = 16
            HEIGHT = 16
            Y_POS_ROW = 16
            NUM_FRAMES = 8

        class Properties:
            SCALE_FACTOR = 2







