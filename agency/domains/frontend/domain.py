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
                return f"""import React, {{ useState }} from 'react';
import './{component_name}.css';

/**
 * {component_name} Component
 * Description: {query}
 */
const {component_name} = ({{ children, className = '', ...props }}) => {{
  const [state, setState] = useState({{}});
  
  const handleClick = (e) => {{
    // Handle click
    console.log('{component_name} clicked');
  }};

  return (
    <div className={`{component_name}-wrapper ${{className}}`} {{...props}}>
      <div className="{component_name}" onClick={{handleClick}}>
        {{children}}
      </div>
    </div>
  );
}};

export default {component_name};
"""
            elif styling_lib == "tailwind":
                return f"""import React, {{ useState }} from 'react';

/**
 * {component_name} Component
 * Description: {query}
 */
const {component_name} = ({{ children, className = '', ...props }}) => {{
  const [state, setState] = useState({{}});
  
  const handleClick = (e) => {{
    // Handle click
    console.log('{component_name} clicked');
  }};

  return (
    <div className={`p-4 bg-white rounded-lg shadow-md ${{className}}`} {{...props}}>
      <div 
        className="bg-gray-100 p-4 rounded border border-gray-200 hover:bg-gray-50 transition-colors cursor-pointer"
        onClick={{handleClick}}
      >
        {{children}}
      </div>
    </div>
  );
}};

export default {component_name};
"""
            else:
                return f"""import React, {{ useState }} from 'react';

/**
 * {component_name} Component
 * Description: {query}
 */
const {component_name} = ({{ children, className = '', ...props }}) => {{
  const [state, setState] = useState({{}});
  
  const handleClick = (e) => {{
    // Handle click
    console.log('{component_name} clicked');
  }};

  return (
    <div className={`{component_name}-wrapper ${{className}}`} {{...props}}>
      <div className="{component_name}" onClick={{handleClick}}>
        {{children}}
      </div>
    </div>
  );
}};

export default {component_name};
"""
        elif framework == "vue":
            return f"""<template>
  <div class="{component_name.toLowerCase()}-wrapper" @click="handleClick">
    <div class="{component_name.toLowerCase()}">
      <slot />
    </div>
  </div>
</template>

<script>
export default {{
  name: '{component_name}',
  props: {{
    // Define props here
  }},
  data() {{
    return {{
      // Component state
    }};
  }},
  methods: {{
    handleClick(event) {{
      // Handle click
      console.log('{component_name} clicked');
    }}
  }},
  mounted() {{
    // Component mounted
  }}
}};
</script>

<style scoped>
.{component_name.lower()}-wrapper {{
  /* Add wrapper styles */
}}

.{component_name.lower()} {{
  /* Add component styles */
}}
</style>
"""
        else:
            return f"// {component_name} component for {query} using {framework}"

    def _generate_page_template(self, query: str, framework: str, styling_lib: str, state_manager: str, params: Dict[str, Any]) -> str:
        """Generate a frontend page based on the query"""
        page_name = params.get("page_name", "HomePage")
        
        if framework == "react":
            if state_manager == "redux":
                return f"""import React from 'react';
import {{ useSelector, useDispatch }} from 'react-redux';
import './{page_name}.css';

/**
 * {page_name} Page
 * Description: {query}
 */
const {page_name} = () => {{
  const dispatch = useDispatch();
  const {page_name.lower()}Data = useSelector(state => state.{page_name.lower()});

  return (
    <div className="{page_name.toLowerCase()}-page">
      <header>
        <h1>{page_name.replace('Page', '')}</h1>
      </header>
      
      <main>
        <p>Welcome to the {page_name.replace('Page', '')} page.</p>
        {/* Add page content here */}
      </main>
      
      <footer>
        <p>&copy; 2023 {page_name.replace('Page', '')}. All rights reserved.</p>
      </footer>
    </div>
  );
}};

export default {page_name};
"""
            else:
                return f"""import React, {{ useState, useEffect }} from 'react';
import './{page_name}.css';

/**
 * {page_name} Page
 * Description: {query}
 */
const {page_name} = () => {{
  const [data, setData] = useState(null);

  useEffect(() => {{
    // Fetch data or perform initialization
    console.log('Loading {page_name} data...');
  }}, []);

  return (
    <div className="{page_name.toLowerCase()}-page">
      <header>
        <h1>{page_name.replace('Page', '')}</h1>
      </header>
      
      <main>
        <p>Welcome to the {page_name.replace('Page', '')} page.</p>
        {/* Add page content here */}
      </main>
      
      <footer>
        <p>&copy; 2023 {page_name.replace('Page', '')}. All rights reserved.</p>
      </footer>
    </div>
  );
}};

export default {page_name};
"""
        elif framework == "nextjs":
            return f"""import React, {{ useState, useEffect }} from 'react';
import Head from 'next/head';

/**
 * {page_name} Page
 * Description: {query}
 */
const {page_name} = () => {{
  const [data, setData] = useState(null);

  useEffect(() => {{
    // Fetch data or perform initialization
    console.log('Loading {page_name} data...');
  }}, []);

  return (
    <div className="{page_name.toLowerCase()}-page">
      <Head>
        <title>{page_name.replace('Page', '')}</title>
        <meta name="description" content="{query}" />
      </Head>
      
      <header>
        <h1>{page_name.replace('Page', '')}</h1>
      </header>
      
      <main>
        <p>Welcome to the {page_name.replace('Page', '')} page.</p>
        {/* Add page content here */}
      </main>
      
      <footer>
        <p>&copy; 2023 {page_name.replace('Page', '')}. All rights reserved.</p>
      </footer>
    </div>
  );
}};

export default {page_name};

// For static generation or server-side rendering
// export async function getStaticProps() {{
//   // Fetch data for the page
//   return {{
//     props: {{}},
//   }};
// }}
"""
        else:
            return f"// {page_name} page for {query} using {framework}"

    def _generate_layout_template(self, query: str, framework: str, styling_lib: str, state_manager: str, params: Dict[str, Any]) -> str:
        """Generate a frontend layout based on the query"""
        layout_name = params.get("layout_name", "MainLayout")
        
        if framework == "react":
            return f"""import React from 'react';
import Navigation from '../components/Navigation';
import Footer from '../components/Footer';
import './{layout_name}.css';

/**
 * {layout_name} Layout
 * Description: {query}
 */
const {layout_name} = ({{ children }}) => {{
  return (
    <div className="{layout_name.toLowerCase()}-container">
      <Navigation />
      
      <main className="{layout_name.toLowerCase()}-main">
        {{children}}
      </main>
      
      <Footer />
    </div>
  );
}};

export default {layout_name};
"""
        elif framework == "nextjs":
            return f"""import React from 'react';
import Navigation from '../components/Navigation';
import Footer from '../components/Footer';

/**
 * {layout_name} Layout
 * Description: {query}
 */
const {layout_name} = ({{ children }}) => {{
  return (
    <div className="{layout_name.toLowerCase()}-container">
      <Navigation />
      
      <main className="{layout_name.toLowerCase()}-main">
        {{children}}
      </main>
      
      <Footer />
    </div>
  );
}};

export default {layout_name};

// If using App Router in Next.js 13+
// export default function RootLayout({{ children }}) {{
//   return (
//     <html lang="en">
//       <body>
//         <{layout_name}>
//           {{children}}
//         </{layout_name}>
//       </body>
//     </html>
//   );
// }}
"""
        else:
            return f"// {layout_name} layout for {query} using {framework}"

    def _generate_hook_template(self, query: str, framework: str, styling_lib: str, state_manager: str, params: Dict[str, Any]) -> str:
        """Generate a frontend hook based on the query"""
        hook_name = params.get("hook_name", "useCustomHook")
        
        if framework == "react":
            return f"""import {{ useState, useEffect, useCallback }} from 'react';

/**
 * Custom Hook: {hook_name}
 * Description: {query}
 */
const {hook_name} = (initialValue = null) => {{
  const [value, setValue] = useState(initialValue);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {{
    setLoading(true);
    setError(null);
    
    try {{
      // Perform async operation
      const result = await fetch('/api/data'); // Replace with actual API call
      const data = await result.json();
      setValue(data);
    }} catch (err) {{
      setError(err.message);
    }} finally {{
      setLoading(false);
    }}
  }}, []);

  const updateValue = useCallback((newValue) => {{
    setValue(newValue);
  }}, []);

  useEffect(() => {{
    // Perform side effects
    fetchData();
  }}, []);

  return {{ value, loading, error, updateValue, fetchData }};
}};

export default {hook_name};
"""
        else:
            return f"// {hook_name} hook for {query} using {framework}"

    def _generate_store_template(self, query: str, framework: str, styling_lib: str, state_manager: str, params: Dict[str, Any]) -> str:
        """Generate a frontend store/state management code based on the query"""
        store_name = params.get("store_name", "appStore")
        
        if state_manager == "redux":
            return f"""// Redux Store for {query}
import {{ configureStore }} from '@reduxjs/toolkit';
import {store_name.lower()}Reducer from './{store_name.lower()}Slice';

export const store = configureStore({{
  reducer: {{
    {store_name.lower()}: {store_name.lower()}Reducer,
    // Add other reducers here
  }},
}});

// Infer the `RootState` and `AppDispatch` types from the store itself
export type RootState = ReturnType<typeof store.getState>;
// Inferred type: {{posts: PostsState, comments: CommentsState, users: UsersState}}
export type AppDispatch = typeof store.dispatch;
"""
        elif state_manager == "zustand":
            return f"""// Zustand Store for {query}
import {{ create }} from 'zustand';
import {{ persist, devtools }} from 'zustand/middleware';

const use{store_name.capitalize()} = create(
  devtools(
    persist(
      (set, get) => ({
        // State
        data: [],
        loading: false,
        error: null,

        // Actions
        setData: (newData) => set({{ data: newData }}),
        setLoading: (isLoading) => set({{ loading: isLoading }}),
        setError: (error) => set({{ error }}),

        // Async actions
        fetchData: async () => {{
          set({{ loading: true, error: null }});
          try {{
            // Replace with actual API call
            const response = await fetch('/api/data');
            const data = await response.json();
            set({{ data, loading: false }});
          }} catch (error) {{
            set({{ error: error.message, loading: false }});
          }}
        }},
      }),
      {{
        name: '{store_name.lower()}-storage', // Unique name for localStorage
      }}
    )
  )
);

export default use{store_name.capitalize()};
"""
        elif state_manager == "context_api":
            return f"""// Context API Store for {query}
import React, {{ createContext, useContext, useReducer }} from 'react';

// Initial state
const initialState = {{
  data: [],
  loading: false,
  error: null,
}};

// Action types
const SET_DATA = 'SET_DATA';
const SET_LOADING = 'SET_LOADING';
const SET_ERROR = 'SET_ERROR';
const FETCH_DATA_START = 'FETCH_DATA_START';
const FETCH_DATA_SUCCESS = 'FETCH_DATA_SUCCESS';
const FETCH_DATA_ERROR = 'FETCH_DATA_ERROR';

// Reducer
const {store_name.lower()}Reducer = (state, action) => {{
  switch (action.type) {{
    case SET_DATA:
      return {{ ...state, data: action.payload }};
    case SET_LOADING:
      return {{ ...state, loading: action.payload }};
    case SET_ERROR:
      return {{ ...state, error: action.payload }};
    case FETCH_DATA_START:
      return {{ ...state, loading: true, error: null }};
    case FETCH_DATA_SUCCESS:
      return {{ ...state, loading: false, data: action.payload, error: null }};
    case FETCH_DATA_ERROR:
      return {{ ...state, loading: false, error: action.payload }};
    default:
      return state;
  }}
}};

// Context
const {store_name.capitalize()}Context = createContext();

// Provider
export const {store_name.capitalize()}Provider = ({{ children }}) => {{
  const [state, dispatch] = useReducer({store_name.lower()}Reducer, initialState);

  const value = {{
    ...state,
    setData: (data) => dispatch({{ type: SET_DATA, payload: data }}),
    setLoading: (loading) => dispatch({{ type: SET_LOADING, payload: loading }}),
    setError: (error) => dispatch({{ type: SET_ERROR, payload: error }}),
    fetchData: async () => {{
      dispatch({{ type: FETCH_DATA_START }});
      try {{
        // Replace with actual API call
        const response = await fetch('/api/data');
        const data = await response.json();
        dispatch({{ type: FETCH_DATA_SUCCESS, payload: data }});
      }} catch (error) {{
        dispatch({{ type: FETCH_DATA_ERROR, payload: error.message }});
      }}
    }}
  }};

  return (
    <{store_name.capitalize()}Context.Provider value={{value}}>
      {{children}}
    </{store_name.capitalize()}Context.Provider>
  );
}};

// Custom hook to use the context
export const use{store_name.capitalize()} = () => {{
  const context = useContext({store_name.capitalize()}Context);
  if (!context) {{
    throw new Error('use{store_name.capitalize()} must be used within a {store_name.capitalize()}Provider');
  }}
  return context;
}};
"""
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