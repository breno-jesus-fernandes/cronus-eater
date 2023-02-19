from typing import Any, Dict, List, Tuple, Union

import numpy as np
import pandas as pd

from cronus_eater import _normalizer, _validator
from cronus_eater.model import TimeSeries, TimeSeriesMetadata


def find_metadata(df: pd.DataFrame, origin: str) -> List[TimeSeriesMetadata]:
    return []


def slice_dataframe(
    df: pd.DataFrame, metadata: List[TimeSeriesMetadata]
) -> List[TimeSeries]:
    return []


def find_header(df: pd.DataFrame, start_row: int, end_column: int) -> int:
    for index, value in df.iloc[start_row - 1 :: -1, end_column].items():
        if _validator.is_date_time(value):
            return int(str(index))

    return -1


def find_end_column(row: pd.Series) -> int:
    last_text_column = -1
    last_number_column = -1

    # If is a empty sequence return false
    if len(row.dropna()) == 0:
        return False

    qtd_text_sequence = 0
    # Calcule the right pattern of a time series row
    for index, value in row.items():
        if (
            _validator.is_text(value) or _validator.is_date_time(value)
        ) and last_number_column == -1:
            last_text_column = int(str(index))
            qtd_text_sequence += 1
        elif _validator.is_financial_number(value) and last_text_column != -1:
            last_number_column = int(str(index))
        elif (
            _validator.is_text(value) or _validator.is_date_time(value)
        ) and last_number_column != -1:
            break

    # if a sequence is empty means we do not have a time series pattern
    if -1 in (last_text_column, last_number_column):
        return -1

    return last_number_column


def find_start_row_index(df: pd.DataFrame, column_index: int) -> int:
    for row_index, row in df.iloc[:, column_index:].iterrows():
        if not pd.isnull(row.iloc[0]):
            if _validator.is_time_series_row(row):
                return int(str(row_index))

    return -1


def find_start_row_column(df: pd.DataFrame) -> Tuple[int, int]:
    for column_index, column in df.items():
        start_column = int(str(column_index))
        if len(column.dropna()) >= 2:
            start_row = find_start_row_index(df, int(str(column_index)))

            if start_row != -1:
                return start_row, start_column

    return -1, -1


def find_end_row_column(
    df: pd.DataFrame, start_row: int, start_column: int
) -> Tuple[int, int]:

    end_column = find_end_column(df.iloc[start_row, start_column:])
    df = df.iloc[start_row:, start_column:end_column].copy()

    end_row = -1
    for row_index, row in df.iterrows():
        if _validator.is_time_series_row(row):
            end_row = int(str(row_index))
        elif _validator.is_text_row(row):
            break

    return end_row, end_column


def clean_garbage_row(row: pd.Series) -> pd.Series:
    qtd_text = row.map(lambda value: _validator.is_text(value)).sum()
    if qtd_text >= 2:
        return row.map(lambda value: pd.NA)
    return row


def to_literal_blank(value: Any) -> Any:
    if pd.isna(value):
        return 'Vazio'
    return value


def clean_time_series_from_raw_df(
    df: pd.DataFrame, metadata: TimeSeriesMetadata
) -> pd.DataFrame:
    df.iloc[
        metadata.start_row : metadata.end_row + 1,
        metadata.start_column : metadata.end_column + 1,
    ] = np.nan
    return df.copy()


def clean_gargabe_column(
    df: pd.DataFrame, start_row: int, start_column: int
) -> pd.DataFrame:

    if start_row == -1 and start_column >= 0:
        df[df.columns[start_column]] = np.nan
        return df.copy()

    return df.copy()


def clean_gargabe_table(
    df: pd.DataFrame,
    start_row: int,
    start_column: int,
    end_row: int,
    end_column: int,
) -> pd.DataFrame:

    if (
        start_row >= 0
        and start_column >= 0
        and end_column >= 0
        and end_row >= 0
    ):
        df.iloc[start_row : end_row + 1, start_column : end_row + 1] = np.nan
        return df.copy()

    return df.copy()


def find_time_series(raw_dataframe: pd.DataFrame) -> pd.DataFrame:

    df = raw_dataframe.copy()
    dfs = []
    df_order = 1
    while True:

        # If there's no more value, finish the search
        tot_not_null = (~df.isnull()).values.sum()
        if tot_not_null == 0:
            break

        start_row, start_column = find_start_row_column(df)

        # If can find start row, clean gargabe column and starts again the search
        if start_row == -1 and start_column >= 0:
            df = clean_gargabe_column(df, start_row, start_column)
            continue
        # If there's no start column finish the search
        elif start_row == -1 and start_column == -1:
            break

        end_row, end_column = find_end_row_column(df, start_row, start_column)

        header_row = find_header(df, start_row, end_column)
        # If can't find a header row clean the table and start again the search
        if header_row == -1:
            df = clean_gargabe_table(
                df, start_row, start_column, end_row, end_column
            )
            continue
        else:
            start_row = header_row

        metadata = TimeSeriesMetadata(
            'whatever',
            'whatever',
            start_column,
            end_column,
            start_row,
            end_row,
        )
        # Copy Time Series From raw dataframe
        time_series_df = df.iloc[
            start_row : end_row + 1, start_column : end_column + 1
        ].copy()

        time_series_df = (
            time_series_df.apply(lambda row: clean_garbage_row(row), axis=1)
            .dropna(how='all', axis=0)
            .dropna(how='all', axis=1)
        )

        time_series_df[time_series_df.columns[0]] = time_series_df[
            time_series_df.columns[0]
        ].map(lambda value: to_literal_blank(value))
        time_series_df = time_series_df.applymap(
            lambda value: _normalizer.norm_blank_value(value)
        )

        time_series_df.iloc[0, 0] = 'Index'
        time_series_df.iloc[0, :] = time_series_df.iloc[0, :].map(
            lambda value: _normalizer.norm_header(value)
        )

        time_series_df = time_series_df.rename(
            columns=time_series_df.iloc[0]
        ).drop(time_series_df.index[0])

        time_series_df.fillna(0, inplace=True)
        time_series_df.reset_index(inplace=True)
        time_series_df.rename(columns={'index': 'Numeric Index'}, inplace=True)

        time_series_df['Order'] = df_order

        time_series_df = pd.melt(
            time_series_df,
            id_vars=['Numeric Index', 'Index', 'Order'],
            var_name='Time',
            value_name='Value',
        )

        dfs.append(time_series_df)

        # Clean Time Series from raw dataframe
        df = clean_time_series_from_raw_df(df, metadata)
        df_order += 1

    if len(dfs) == 0:
        return pd.DataFrame()

    return pd.concat(dfs, ignore_index=True)


def find_all_time_series(
    raw_dataframes: Dict[Union[int, str], pd.DataFrame]
) -> pd.DataFrame:
    all_time_series = []

    for sheet_name, raw_df in raw_dataframes.items():
        df = find_time_series(raw_df)
        if not df.empty:
            df['Sheet Name'] = sheet_name
            all_time_series.append(df)

    return pd.concat(all_time_series, ignore_index=True)