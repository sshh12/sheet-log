# sheet-log

## Install

1. `pip install git+https://github.com/sshh12/sheet-log`
2. Create a script on [script.google.com](https://script.google.com/), copy-paste the contents of `Code.gs`, then deploy (`Execute as=Me`, `Who has access=Anyone`) as web-app.
3. Create a [google sheet](https://sheet.new) that includes a tab named `sheetlog`. This is to ensure the web-app only modifies spreadsheets that are used by this app.

## Usage

### Scikit-learn GridCV Table

```python
from sklearn.datasets import make_classification
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC

from sheetlog import SheetLog

sl = SheetLog(
    app_url="https://script.google.com/macros/s/.../exec",
    spreadsheet_id="5F31_GE54Vi_....",
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

### Scikit-learn TSNE Tabs

```python
from sklearn import manifold, datasets
import matplotlib.pyplot as plt
import numpy as np
import time

from sheetlog import SheetLog

sl = SheetLog(
    app_url="https://script.google.com/macros/s/AKfycbwbat9Z8zGyUy6DoHljNrKJlaECdAwCGKPHzMfsKGuiuILV8gOyJqDubWVg4UOeHy6y9g/exec",
    spreadsheet_id="1Zhc_GvozVi_XaCICcmShRdczeq6NgZkmo3QnW4X_CGg",
)

n_samples = 300
n_components = 2
perplexities = [5, 30, 50, 100]

X, y = datasets.make_circles(n_samples=n_samples, factor=0.5, noise=0.05)

red = y == 0
green = y == 1

for i, perplexity in enumerate(perplexities):
    t0 = time.time()
    tsne = manifold.TSNE(n_components=n_components, init="random", random_state=0, perplexity=perplexity)
    Y = tsne.fit_transform(X)
    t1 = time.time()
    name = "circles, perplexity=%d in %.2g sec" % (perplexity, t1 - t0)
    plt.title("Perplexity=%d" % perplexity)
    plt.scatter(Y[red, 0], Y[red, 1], c="r")
    plt.scatter(Y[green, 0], Y[green, 1], c="g")
    plt.axis("tight")
    sl.add(dict(perplexity=perplexity, time=t1 - t0, plot=sl.get_current_plot()), sheet=name)

X, color = datasets.make_s_curve(n_samples, random_state=0)

for i, perplexity in enumerate(perplexities):
    t0 = time.time()
    tsne = manifold.TSNE(n_components=n_components, init="random", random_state=0, perplexity=perplexity)
    Y = tsne.fit_transform(X)
    t1 = time.time()
    name = "S-curve, perplexity=%d in %.2g sec" % (perplexity, t1 - t0)
    plt.title("Perplexity=%d" % perplexity)
    plt.scatter(Y[:, 0], Y[:, 1], c=color)
    plt.axis("tight")
    sl.add(dict(perplexity=perplexity, time=t1 - t0, plot=sl.get_current_plot()), sheet=name)

x = np.linspace(0, 1, int(np.sqrt(n_samples)))
xx, yy = np.meshgrid(x, x)
X = np.hstack(
    [
        xx.ravel().reshape(-1, 1),
        yy.ravel().reshape(-1, 1),
    ]
)
color = xx.ravel()

for i, perplexity in enumerate(perplexities):
    t0 = time.time()
    tsne = manifold.TSNE(n_components=n_components, init="random", random_state=0, perplexity=perplexity)
    Y = tsne.fit_transform(X)
    t1 = time.time()
    name = "uniform grid, perplexity=%d in %.2g sec" % (perplexity, t1 - t0)
    plt.title("Perplexity=%d" % perplexity)
    plt.scatter(Y[:, 0], Y[:, 1], c=color)
    plt.axis("tight")
    sl.add(dict(perplexity=perplexity, time=t1 - t0, plot=sl.get_current_plot()), sheet=name)
```

![scikit learn example 2](https://user-images.githubusercontent.com/6625384/120231093-42c1d380-c216-11eb-925b-ebf708313179.gif)
