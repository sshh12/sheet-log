# sheet-log

## Install

1. `pip install git+https://github.com/sshh12/sheet-log`
2. Create a script on [script.google.com](https://script.google.com/), copy-paste the contents of `Code.gs`, then deploy (`Execute as=Me`, `Who has access=Anyone`) as web-app.
3. Create a google sheet that include a tab named `sheetlog`. This is to ensure the web-app only modifies spreadsheets that are used by this app.

## Usage

### Scikit-learn GridCV

```python
from sklearn.datasets import make_classification
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC

from sheetlog import SheetLog

sl = SheetLog(
    app_url="https://script.google.com/macros/s/.../exec",
    spreadsheet_id="...",
)

param_grid = {"kernel": ("linear", "rbf"), "C": [1, 10, 100]}
base_estimator = SVC(gamma="scale")
X, y = make_classification(n_samples=1000)
gcv = GridSearchCV(base_estimator, param_grid, cv=5)
gcv.fit(X, y)

for params, mean_test_score, rank_test_score in zip(
    gcv.cv_results_["params"], gcv.cv_results_["mean_test_score"], gcv.cv_results_["rank_test_score"]
):
    sl.add(dict(**params, test_score=mean_test_score, rank_score=rank_test_score))
```

![scikit learn example](https://user-images.githubusercontent.com/6625384/120229535-f6c15f80-c212-11eb-8ac8-53aa570a1187.png)
