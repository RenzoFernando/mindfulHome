import { createSlice } from "@reduxjs/toolkit";

const initialState = {
token: localStorage.getItem("token") || null,
user: null,
isAuthenticated: !!localStorage.getItem("token"),
loading: false,
};

const userSlice = createSlice({
name: "user",
initialState,
reducers: {
setToken: (state, action) => {
state.token = action.payload;
state.isAuthenticated = true;

        localStorage.setItem("token", action.payload);
    },

    setUser: (state, action) => {
        state.user = action.payload;
    },

    setLoading: (state, action) => {
        state.loading = action.payload;
    },

    clearUserData: (state) => {
        state.token = null;
        state.user = null;
        state.isAuthenticated = false;

        localStorage.removeItem("token");
    },

    updateUserProfile: (state, action) => {
        state.user = {
            ...state.user,
            ...action.payload,
        };
    },

    logout: (state) => {
    state.token = null;
    state.user = null;
    state.isAuthenticated = false;

    localStorage.removeItem("token");
},
},

});

export const {
setToken,
setUser,
setLoading,
clearUserData,
updateUserProfile,
logout,
} = userSlice.actions;

export default userSlice.reducer;