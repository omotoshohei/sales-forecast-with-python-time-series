from __future__ import annotations

import sys
import types

import pandas as pd
import pytest

from sales_forecast.data import standardize_sales_data
from sales_forecast.features import build_features, model_ready
from sales_forecast.models.lightgbm import LightGBMForecastModel
from sales_forecast.models.optional import import_optional_dependency
from sales_forecast.models.prophet import ProphetForecastModel
from sales_forecast.models.registry import create_model
from sales_forecast.models.sarimax import SarimaxForecastModel


class FakeLGBMRegressor:
    def fit(self, features: pd.DataFrame, target: pd.Series) -> None:
        self.value = float(target.mean())

    def predict(self, features: pd.DataFrame) -> list[float]:
        return [self.value] * len(features)


class FakeProphet:
    def __init__(self, **parameters):
        self.parameters = parameters
        self.regressors = []
        self.value = 0.0

    def add_regressor(self, name: str) -> None:
        self.regressors.append(name)

    def fit(self, frame: pd.DataFrame) -> None:
        self.value = float(frame["y"].mean())

    def predict(self, frame: pd.DataFrame) -> pd.DataFrame:
        return pd.DataFrame({"yhat": [self.value] * len(frame)})


class FakeSarimaxModel:
    def __init__(self, endog, exog=None, **parameters):
        self.value = float(endog.mean())

    def fit(self, disp: bool = False):
        return FakeSarimaxResult(self.value)


class FakeSarimaxResult:
    def __init__(self, value: float) -> None:
        self.value = value

    def forecast(self, steps: int, exog=None) -> pd.Series:
        return pd.Series([self.value] * steps)


@pytest.fixture
def featured_sales(raw_sales, data_config) -> pd.DataFrame:
    df = standardize_sales_data(raw_sales, data_config)
    return model_ready(build_features(df, data_config), data_config, require_target=False)


def test_optional_dependency_error_mentions_install_extra(monkeypatch):
    monkeypatch.setitem(sys.modules, "missing_optional_package", None)

    with pytest.raises(ValueError, match='pip install -e "\\.\\[extra\\]"'):
        import_optional_dependency("missing_optional_package", "example", "extra")


def test_registry_creates_optional_models(data_config):
    assert isinstance(create_model("lightgbm", data_config), LightGBMForecastModel)
    assert isinstance(create_model("prophet", data_config), ProphetForecastModel)
    assert isinstance(create_model("sarimax", data_config), SarimaxForecastModel)


def test_lightgbm_model_fits_and_predicts_with_optional_module(
    monkeypatch, featured_sales, data_config
):
    fake_module = types.SimpleNamespace(LGBMRegressor=lambda **parameters: FakeLGBMRegressor())
    monkeypatch.setitem(sys.modules, "lightgbm", fake_module)
    model = LightGBMForecastModel(data_config=data_config)

    model.fit(featured_sales.iloc[:20])
    prediction = model.predict(featured_sales.iloc[20:23])

    assert prediction.name == "prediction"
    assert prediction.tolist() == [1009.5, 1009.5, 1009.5]


def test_prophet_model_fits_and_predicts_with_optional_module(
    monkeypatch, featured_sales, data_config
):
    fake_module = types.SimpleNamespace(Prophet=FakeProphet)
    monkeypatch.setitem(sys.modules, "prophet", fake_module)
    model = ProphetForecastModel(data_config=data_config)

    model.fit(featured_sales.iloc[:20])
    prediction = model.predict(featured_sales.iloc[20:23])

    assert prediction.name == "prediction"
    assert prediction.tolist() == [1009.5, 1009.5, 1009.5]


def test_sarimax_model_fits_and_predicts_with_optional_module(
    monkeypatch, featured_sales, data_config
):
    fake_module = types.SimpleNamespace(SARIMAX=FakeSarimaxModel)
    monkeypatch.setitem(sys.modules, "statsmodels.tsa.statespace.sarimax", fake_module)
    model = SarimaxForecastModel(data_config=data_config)

    model.fit(featured_sales.iloc[:20])
    prediction = model.predict(featured_sales.iloc[20:23])

    assert prediction.name == "prediction"
    assert prediction.tolist() == [1009.5, 1009.5, 1009.5]


@pytest.mark.parametrize(
    "model",
    [
        LightGBMForecastModel,
        ProphetForecastModel,
        SarimaxForecastModel,
    ],
)
def test_optional_models_reject_predict_before_fit(model, featured_sales, data_config):
    with pytest.raises(ValueError, match="Model is not fitted."):
        model(data_config=data_config).predict(featured_sales.iloc[:2])
