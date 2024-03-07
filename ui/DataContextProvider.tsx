import React, { useState, useEffect } from 'react';
import { TableData } from "./components/TableData";
import DataContext from "./DataContext";

const DataContextProvider: React.FC = ({ children }) => {
    const [data, setData] = useState<TableData>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    useEffect(() => {
        fetch('/api/object_details/')  // Adjust this URL as needed
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then((fetchedData: TableData) => {
                setData(fetchedData);
                setIsLoading(false);
            })
            .catch(err => {
                setError(err);
                setIsLoading(false);
            });
    }, []);

    return (
        <DataContext.Provider value={{ data, setData, isLoading, error }}>
            {children}
        </DataContext.Provider>
    );
}

export { DataContextProvider };
