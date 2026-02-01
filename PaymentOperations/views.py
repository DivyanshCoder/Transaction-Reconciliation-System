from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from .services import main


ALLOWED_EXTENSIONS = ('.xls', '.xlsx')

def upload_files(request):
    if request.method == "POST":
        statement_file = request.FILES.get("statement_file")
        settlement_file = request.FILES.get("settlement_file")

        # Validate both files exist
        if not statement_file or not settlement_file:
            return render(request, "upload.html", {
                "error": "Both Statement and Settlement files are required."
            })

        # Validate file extensions
        if (not statement_file.name.endswith(ALLOWED_EXTENSIONS) or
            not settlement_file.name.endswith(ALLOWED_EXTENSIONS)):
            return render(request, "upload.html", {
                "error": "Only Excel files (.xls, .xlsx) are allowed."
            })

        # 3️⃣ Save files
        fs = FileSystemStorage(location="media/uploads/")
        statement_path = fs.save(statement_file.name, statement_file)
        settlement_path = fs.save(settlement_file.name, settlement_file)

        result = main()  # Call the main function to process files
        return render(request, "results.html", result)

    return render(request, "upload.html")
