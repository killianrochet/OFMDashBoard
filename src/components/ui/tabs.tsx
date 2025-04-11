import React, { useState, ReactNode } from 'react';

interface TabsProps {
  defaultValue: string;
  children: ReactNode;
  className?: string;
}

interface TabsContextProps {
  value: string;
  setValue: (val: string) => void;
}

const TabsContext = React.createContext<TabsContextProps | null>(null);

export function Tabs({ defaultValue, children, className = '' }: TabsProps) {
  const [value, setValue] = useState(defaultValue);

  return (
    <TabsContext.Provider value={{ value, setValue }}>
      <div className={className}>{children}</div>
    </TabsContext.Provider>
  );
}

interface TabsListProps {
  children: ReactNode;
  className?: string;
}

export function TabsList({ children, className = '' }: TabsListProps) {
  return <div className={`flex space-x-2 border-b pb-2 mb-4 ${className}`}>{children}</div>;
}

interface TabsTriggerProps {
  value: string;
  children: ReactNode;
}

export function TabsTrigger({ value, children }: TabsTriggerProps) {
  const ctx = React.useContext(TabsContext);
  if (!ctx) return null;

  const active = ctx.value === value;

  return (
    <button
      onClick={() => ctx.setValue(value)}
      className={`px-4 py-2 text-sm font-medium rounded-t-md ${
        active ? 'border-b-2 border-black' : 'text-gray-500'
      }`}
    >
      {children}
    </button>
  );
}

interface TabsContentProps {
  value: string;
  children: ReactNode;
}

export function TabsContent({ value, children }: TabsContentProps) {
  const ctx = React.useContext(TabsContext);
  if (!ctx || ctx.value !== value) return null;

  return <div>{children}</div>;
}
