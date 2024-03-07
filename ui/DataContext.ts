import React from 'react';
import { TableData } from "./components/TableData";

type DataContextType = {
  data: TableData;
  setData: React.Dispatch<React.SetStateAction<TableData>>;
  isLoading: boolean;
  error: Error | null;
};

const DataContext = React.createContext<DataContextType | undefined>(undefined);

export default DataContext;
