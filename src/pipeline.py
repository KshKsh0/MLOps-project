from .schema import (
    create_schema,
    create_feature_views,
)

from .ingest import ingest_all

from .validate import validate


def main():

    print(
        """
=========================================
       OLIST DATA PIPELINE
=========================================
"""
    )



    print(
        "[1/4] Creating database schema..."
    )

    create_schema()



    print(
        "\n[2/4] Ingesting CSV files..."
    )

    ingest_all()


    print(
        "\n[3/4] Creating analytics views..."
    )

    create_feature_views()




    print(
        "\n[4/4] Validating pipeline..."
    )

    validate()


    print(
        """
=========================================
       PIPELINE COMPLETED
=========================================
"""
    )


if __name__ == "__main__":

    main()