from typing import Dict, Any
from ...core.base_domain import BaseDomain, DomainInput, DomainOutput
import json


class FrontendDomain(BaseDomain):
    """Domain responsible for frontend development including UI/UX, frameworks, and client-side logic"""

    def __init__(self, name: str = "frontend", description: str = "Develops frontend applications using modern frameworks and UI/UX best practices", resource_manager=None, cache_enabled: bool = True):
        super().__init__(name=name, description=description, resource_manager=resource_manager, cache_enabled=cache_enabled)
        self.frameworks = ["react", "vue", "angular", "svelte", "nextjs", "nuxt", "gatsby", "remix"]
        self.styling_libs = ["css", "scss", "tailwind", "bootstrap", "material_ui", "chakra_ui", "emotion"]
        self.state_managers = ["redux", "zustand", "mobx", "vuex", "pinia", "context_api"]
        self.testing_libs = ["jest", "cypress", "storybook", "testing_library", "enzyme"]
        self.frontend_templates = {
            "component": self._generate_component_template,
            "page": self._generate_page_template,
            "layout": self._generate_layout_template,
            "hook": self._generate_hook_template,
            "store": self._generate_store_template
        }

    async def execute(self, input_data: DomainInput) -> DomainOutput:
        """Generate frontend code based on the input specification"""
        try:
            # Acquire resources before executing
            if not await self.resource_manager.acquire_resources(self.name):
                return DomainOutput(
                    success=False,
                    error=f"Resource limits exceeded for domain {self.name}"
                )

            try:
                query = input_data.query.lower()
                context = input_data.context
                params = input_data.parameters

                # Determine the type of frontend code to generate
                frontend_type = self._determine_frontend_type(query)
                framework = params.get("framework", context.get("framework", "react"))
                styling_lib = params.get("styling_lib", context.get("styling_lib", "css"))
                state_manager = params.get("state_manager", context.get("state_manager", "context_api"))

                if framework not in self.frameworks:
                    return DomainOutput(
                        success=False,
                        error=f"Framework '{framework}' not supported. Available frameworks: {', '.join(self.frameworks)}"
                    )

                # Generate the frontend code
                generated_code = self._generate_frontend_code(frontend_type, query, framework, styling_lib, state_manager, params)

                # Enhance the code if other domains are available
                enhanced_code = await self._enhance_with_other_domains(generated_code, input_data)

                return DomainOutput(
                    success=True,
                    data={
                        "code": enhanced_code,
                        "framework": framework,
                        "styling_lib": styling_lib,
                        "state_manager": state_manager,
                        "type": frontend_type,
                        "original_query": query
                    },
                    metadata={
                        "domain": self.name,
                        "enhanced": enhanced_code != generated_code
                    }
                )
            finally:
                # Always release resources after execution
                self.resource_manager.release_resources(self.name)
        except Exception as e:
            return DomainOutput(
                success=False,
                error=f"Frontend code generation failed: {str(e)}"
            )

    def can_handle(self, input_data: DomainInput) -> bool:
        """Determine if this domain can handle the input"""
        query = input_data.query.lower()

        # Check for keywords that suggest frontend development
        frontend_keywords = [
            "frontend", "ui", "ux", "user interface", "user experience", 
            "react", "vue", "angular", "svelte", "nextjs", "nuxt", 
            "component", "page", "layout", "hook", "store", "state", 
            "front-end", "client-side", "web application", "mobile app", 
            "responsive design", "css", "scss", "tailwind", "bootstrap", 
            "material ui", "chakra ui", "styled components", "theme", 
            "navigation", "header", "footer", "sidebar", "modal", "dialog", 
            "form", "input", "button", "card", "grid", "flexbox"
        ]

        return any(keyword in query for keyword in frontend_keywords)

    def _determine_frontend_type(self, query: str) -> str:
        """Determine what type of frontend code to generate based on the query"""
        if any(word in query for word in ["component", "ui component", "widget", "element"]):
            return "component"
        elif any(word in query for word in ["page", "screen", "view", "route"]):
            return "page"
        elif any(word in query for word in ["layout", "template", "structure", "scaffold"]):
            return "layout"
        elif any(word in query for word in ["hook", "custom hook", "use", "react hook"]):
            return "hook"
        elif any(word in query for word in ["store", "state", "redux", "context", "zustand"]):
            return "store"
        else:
            return "component"  # Default to component

    def _generate_frontend_code(self, frontend_type: str, query: str, framework: str, styling_lib: str, state_manager: str, params: Dict[str, Any]) -> str:
        """Generate frontend code based on type, query, and framework"""
        if frontend_type in self.frontend_templates:
            return self.frontend_templates[frontend_type](query, framework, styling_lib, state_manager, params)
        else:
            return self._generate_generic_frontend_code(query, frontend_type, framework, styling_lib, state_manager, params)

    def _generate_component_template(self, query: str, framework: str, styling_lib: str, state_manager: str, params: Dict[str, Any]) -> str:
        """Generate a frontend component based on the query"""
        component_name = params.get("component_name", "MyComponent")
        
        if framework == "react":
            if styling_lib == "css":
                template = """import React, { useState } from 'react';
import './COMPONENT_NAME.css';

/**
 * COMPONENT_NAME Component
 * Description: QUERY
 */
const COMPONENT_NAME = ({ children, className = '', ...props }) => {
  const [state, setState] = useState({});

  const handleClick = (e) => {
    // Handle click
    console.log('COMPONENT_NAME clicked');
  };

  return (
    <div className={`${COMPONENT_NAME}-wrapper ${className}`} {...props}>
      <div className="COMPONENT_NAME" onClick={handleClick}>
        {children}
      </div>
    </div>
  );
};

export default COMPONENT_NAME;
"""
                return template.replace('COMPONENT_NAME', component_name).replace('QUERY', query)
            elif styling_lib == "tailwind":
                template = """import React, { useState } from 'react';

/**
 * COMPONENT_NAME Component
 * Description: QUERY
 */
const COMPONENT_NAME = ({ children, className = '', ...props }) => {
  const [state, setState] = useState({});

  const handleClick = (e) => {
    // Handle click
    console.log('COMPONENT_NAME clicked');
  };

  return (
    <div className={`p-4 bg-white rounded-lg shadow-md ${className}`} {...props}>
      <div
        className="bg-gray-100 p-4 rounded border border-gray-200 hover:bg-gray-50 transition-colors cursor-pointer"
        onClick={handleClick}
      >
        {children}
      </div>
    </div>
  );
};

export default COMPONENT_NAME;
"""
                return template.replace('COMPONENT_NAME', component_name).replace('QUERY', query)
            else:
                template = """import React, { useState } from 'react';

/**
 * COMPONENT_NAME Component
 * Description: QUERY
 */
const COMPONENT_NAME = ({ children, className = '', ...props }) => {
  const [state, setState] = useState({});

  const handleClick = (e) => {
    // Handle click
    console.log('COMPONENT_NAME clicked');
  };

  return (
    <div className={`${COMPONENT_NAME}-wrapper ${className}`} {...props}>
      <div className="COMPONENT_NAME" onClick={handleClick}>
        {children}
      </div>
    </div>
  );
};

export default COMPONENT_NAME;
"""
                return template.replace('COMPONENT_NAME', component_name).replace('QUERY', query)
        elif framework == "vue":
            template = """<template>
  <div class="COMPONENT_NAME_WRAPPER" @click="handleClick">
    <div class="COMPONENT_NAME">
      <slot />
    </div>
  </div>
</template>

<script>
export default {
  name: 'COMPONENT_NAME',
  props: {
    // Define props here
  },
  data() {
    return {
      // Component state
    };
  },
  methods: {
    handleClick(event) {
      // Handle click
      console.log('COMPONENT_NAME clicked');
    }
  },
  mounted() {
    // Component mounted
  }
};
</script>

<style scoped>
.COMPONENT_NAME_WRAPPER {
  /* Add wrapper styles */
}

.COMPONENT_NAME {
  /* Add component styles */
}
</style>
"""
            return template.replace('COMPONENT_NAME', component_name.lower()).replace('COMPONENT_NAME_WRAPPER', f"{component_name.lower()}-wrapper")
        else:
            return f"// {component_name} component for {query} using {framework}"

    def _generate_page_template(self, query: str, framework: str, styling_lib: str, state_manager: str, params: Dict[str, Any]) -> str:
        """Generate a frontend page based on the query"""
        page_name = params.get("page_name", "HomePage")
        
        if framework == "react":
            if state_manager == "redux":
                template = """import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import './PAGE_NAME.css';

/**
 * PAGE_NAME Page
 * Description: QUERY
 */
const PAGE_NAME = () => {
  const dispatch = useDispatch();
  const PAGEDATA_NAME = useSelector(state => state.PAGEDATA_NAME);

  return (
    <div className="page_name-page">
      <header>
        <h1>PAGE_TITLE</h1>
      </header>

      <main>
        <p>Welcome to the PAGE_TITLE page.</p>
        {/* Add page content here */}
      </main>

      <footer>
        <p>&copy; 2023 PAGE_TITLE. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default PAGE_NAME;
"""
                page_title = page_name.replace('Page', '')
                return template.replace('PAGE_NAME', page_name).replace('QUERY', query).replace('PAGE_TITLE', page_title).replace('PAGEDATA_NAME', f"{page_name.lower()}Data")
            else:
                template = """import React, { useState, useEffect } from 'react';
import './PAGE_NAME.css';

/**
 * PAGE_NAME Page
 * Description: QUERY
 */
const PAGE_NAME = () => {
  const [data, setData] = useState(null);

  useEffect(() => {
    // Fetch data or perform initialization
    console.log('Loading PAGE_NAME data...');
  }, []);

  return (
    <div className="page_name-page">
      <header>
        <h1>PAGE_TITLE</h1>
      </header>

      <main>
        <p>Welcome to the PAGE_TITLE page.</p>
        {/* Add page content here */}
      </main>

      <footer>
        <p>&copy; 2023 PAGE_TITLE. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default PAGE_NAME;
"""
                page_title = page_name.replace('Page', '')
                return template.replace('PAGE_NAME', page_name).replace('QUERY', query).replace('PAGE_TITLE', page_title)
        elif framework == "nextjs":
            template = """import React, { useState, useEffect } from 'react';
import Head from 'next/head';

/**
 * PAGE_NAME Page
 * Description: QUERY
 */
const PAGE_NAME = () => {
  const [data, setData] = useState(null);

  useEffect(() => {
    // Fetch data or perform initialization
    console.log('Loading PAGE_NAME data...');
  }, []);

  return (
    <div className="page_name-page">
      <Head>
        <title>PAGE_TITLE</title>
        <meta name="description" content="QUERY" />
      </Head>

      <header>
        <h1>PAGE_TITLE</h1>
      </header>

      <main>
        <p>Welcome to the PAGE_TITLE page.</p>
        {/* Add page content here */}
      </main>

      <footer>
        <p>&copy; 2023 PAGE_TITLE. All rights reserved.</p>
      </footer>
    </div>
  );
};
export default PAGE_NAME;

// For static generation or server-side rendering
// export async function getStaticProps() {
//   // Fetch data for the page
//   return {
//     props: {},
//   };
// }
"""
        else:
            return f"// {page_name} page for {query} using {framework}"

    def _generate_layout_template(self, query: str, framework: str, styling_lib: str, state_manager: str, params: Dict[str, Any]) -> str:
        """Generate a frontend layout based on the query"""
        layout_name = params.get("layout_name", "MainLayout")
        
        if framework == "react":
            template = """import React from 'react';
import Navigation from '../components/Navigation';
import Footer from '../components/Footer';
import './LAYOUT_NAME.css';

/**
 * LAYOUT_NAME Layout
 * Description: QUERY
 */
const LAYOUT_NAME = ({ children }) => {
  return (
    <div className="layout_name-container">
      <Navigation />

      <main className="layout_name-main">
        {children}
      </main>

      <Footer />
    </div>
  );
};

export default LAYOUT_NAME;
"""
            return template.replace('LAYOUT_NAME', layout_name).replace('QUERY', query)
        elif framework == "nextjs":
            template = """import React from 'react';
import Navigation from '../components/Navigation';
import Footer from '../components/Footer';

/**
 * LAYOUT_NAME Layout
 * Description: QUERY
 */
const LAYOUT_NAME = ({ children }) => {
  return (
    <div className="layout_name-container">
      <Navigation />

      <main className="layout_name-main">
        {children}
      </main>

      <Footer />
    </div>
  );
};

export default LAYOUT_NAME;

// If using App Router in Next.js 13+
// export default function RootLayout({ children }) {
//   return (
//     <html lang="en">
//       <body>
//         <LAYOUT_NAME>
//           {children}
//         </LAYOUT_NAME>
//       </body>
//     </html>
//   );
// }
"""
            return template.replace('LAYOUT_NAME', layout_name).replace('QUERY', query)
        else:
            return f"// {layout_name} layout for {query} using {framework}"

    def _generate_hook_template(self, query: str, framework: str, styling_lib: str, state_manager: str, params: Dict[str, Any]) -> str:
        """Generate a frontend hook based on the query"""
        hook_name = params.get("hook_name", "useCustomHook")
        
        if framework == "react":
            template = """import { useState, useEffect, useCallback } from 'react';

/**
 * Custom Hook: HOOK_NAME
 * Description: QUERY
 */
const HOOK_NAME = (initialValue = null) => {
  const [value, setValue] = useState(initialValue);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      // Perform async operation
      const result = await fetch('/api/data'); // Replace with actual API call
      const data = await result.json();
      setValue(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const updateValue = useCallback((newValue) => {
    setValue(newValue);
  }, []);

  useEffect(() => {
    // Perform side effects
    fetchData();
  }, []);

  return { value, loading, error, updateValue, fetchData };
};

export default HOOK_NAME;
"""
            return template.replace('HOOK_NAME', hook_name).replace('QUERY', query)
        else:
            return f"// {hook_name} hook for {query} using {framework}"

    def _generate_store_template(self, query: str, framework: str, styling_lib: str, state_manager: str, params: Dict[str, Any]) -> str:
        """Generate a frontend store/state management code based on the query"""
        store_name = params.get("store_name", "appStore")
        
        if state_manager == "redux":
            template = """// Redux Store for QUERY
import { configureStore } from '@reduxjs/toolkit';
import STORE_NAME_REDUCER from './STORE_NAMESLICE';

export const store = configureStore({
  reducer: {
    STORE_NAMEDATA: STORE_NAME_REDUCER,
    // Add other reducers here
  },
});

// Infer the `RootState` and `AppDispatch` types from the store itself
export type RootState = ReturnType<typeof store.getState>;
// Inferred type: {posts: PostsState, comments: CommentsState, users: UsersState}
export type AppDispatch = typeof store.dispatch;
"""
            store_lower = store_name.lower()
            return template.replace('QUERY', query).replace('STORE_NAME', store_name).replace('STORE_NAMESLICE', f"{store_lower}Slice").replace('STORE_NAME_REDUCER', f"{store_lower}Reducer").replace('STORE_NAMEDATA', store_lower)
        elif state_manager == "zustand":
            template = """// Zustand Store for QUERY
import { create } from 'zustand';
import { persist, devtools } from 'zustand/middleware';

const useSTORE_NAME_CAPITALIZE = create(
  devtools(
    persist(
      (set, get) => ({
        // State
        data: [],
        loading: false,
        error: null,

        // Actions
        setData: (newData) => set({ data: newData }),
        setLoading: (isLoading) => set({ loading: isLoading }),
        setError: (error) => set({ error }),

        // Async actions
        fetchData: async () => {
          set({ loading: true, error: null });
          try {
            // Replace with actual API call
            const response = await fetch('/api/data');
            const data = await response.json();
            set({ data, loading: false });
          } catch (error) {
            set({ error: error.message, loading: false });
          }
        },
      }),
      {
        name: 'STORE_NAME_LOWER-storage', // Unique name for localStorage
      }
    )
  )
);

export default useSTORE_NAME_CAPITALIZE;
"""
            return template.replace('QUERY', query).replace('STORE_NAME_CAPITALIZE', store_name.capitalize()).replace('STORE_NAME_LOWER', store_name.lower())
        elif state_manager == "context_api":
            template = """// Context API Store for QUERY
import React, { createContext, useContext, useReducer } from 'react';

// Initial state
const initialState = {
  data: [],
  loading: false,
  error: null,
};

// Action types
const SET_DATA = 'SET_DATA';
const SET_LOADING = 'SET_LOADING';
const SET_ERROR = 'SET_ERROR';
const FETCH_DATA_START = 'FETCH_DATA_START';
const FETCH_DATA_SUCCESS = 'FETCH_DATA_SUCCESS';
const FETCH_DATA_ERROR = 'FETCH_DATA_ERROR';

// Reducer
const STORE_NAME_REDUCER = (state, action) => {
  switch (action.type) {
    case SET_DATA:
      return { ...state, data: action.payload };
    case SET_LOADING:
      return { ...state, loading: action.payload };
    case SET_ERROR:
      return { ...state, error: action.payload };
    case FETCH_DATA_START:
      return { ...state, loading: true, error: null };
    case FETCH_DATA_SUCCESS:
      return { ...state, loading: false, data: action.payload, error: null };
    case FETCH_DATA_ERROR:
      return { ...state, loading: false, error: action.payload };
    default:
      return state;
  }
};

// Context
const STORE_NAME_CONTEXT = createContext();

// Provider
export const STORE_NAME_PROVIDER = ({ children }) => {
  const [state, dispatch] = useReducer(STORE_NAME_REDUCER, initialState);

  const value = {
    ...state,
    setData: (data) => dispatch({ type: SET_DATA, payload: data }),
    setLoading: (loading) => dispatch({ type: SET_LOADING, payload: loading }),
    setError: (error) => dispatch({ type: SET_ERROR, payload: error }),
    fetchData: async () => {
      dispatch({ type: FETCH_DATA_START });
      try {
        // Replace with actual API call
        const response = await fetch('/api/data');
        const data = await response.json();
        dispatch({ type: FETCH_DATA_SUCCESS, payload: data });
      } catch (error) {
        dispatch({ type: FETCH_DATA_ERROR, payload: error.message });
      }
    }
  };

  return (
    <STORE_NAME_CONTEXT.Provider value={value}>
      {children}
    </STORE_NAME_CONTEXT.Provider>
  );
};

// Custom hook to use the context
export const useSTORE_NAME_CAPITALIZE = () => {
  const context = useContext(STORE_NAME_CONTEXT);
  if (!context) {
    throw new Error('useSTORE_NAME_CAPITALIZE must be used within a STORE_NAME_PROVIDER');
  }
  return context;
};
"""
            store_lower = store_name.lower()
            store_capitalize = store_name.capitalize()
            return template.replace('QUERY', query).replace('STORE_NAME_REDUCER', f"{store_lower}Reducer").replace('STORE_NAME_CONTEXT', f"{store_capitalize}Context").replace('STORE_NAME_PROVIDER', f"{store_capitalize}Provider").replace('STORE_NAME_CAPITALIZE', store_capitalize)
        else:
            return f"// Store for {query} using {state_manager}"

    def _generate_generic_frontend_code(self, query: str, frontend_type: str, framework: str, styling_lib: str, state_manager: str, params: Dict[str, Any]) -> str:
        """Generate generic frontend code when specific type isn't determined"""
        return f"""// {frontend_type.title()} for {query}
// Framework: {framework}
// Styling: {styling_lib}
// State Management: {state_manager}

// TODO: Implement the {frontend_type} based on the requirements
"""

    async def _enhance_with_other_domains(self, generated_code: str, input_data: DomainInput) -> str:
        """Allow other domains to enhance the generated frontend code"""
        # In a real implementation, this would coordinate with other domains
        # For now, we'll just return the original code
        return generated_code