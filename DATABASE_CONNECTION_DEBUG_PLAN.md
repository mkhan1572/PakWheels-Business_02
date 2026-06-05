# Database Connection Issues - Implementation Plan
**Date:** June 1, 2026  
**Status:** Draft  
**Project:** PakWheels Vehicle Market Analytics System

---

## Executive Summary
The Flask backend is running successfully on `http://localhost:5000`, but multiple database endpoints are returning **500 errors**:
- `/api/analytics/overview` ❌
- `/api/analytics/trends` ❌
- `/api/analytics/cities` ❌

Working endpoints:
- `/api/analytics/top-makes` ✅
- Root dashboard `/` ✅
- Static assets ✅
- Health check endpoint ✅

---

## Main Database Connection Issues to Tackle

### **Issue #1: Database May Not Be Initialized**
**Priority:** CRITICAL  
**Symptoms:** Connection fails or tables don't exist  
**Root Cause:** MySQL database `pakwheels_db` not created or SQL initialization scripts not executed  
**Impact:** All endpoints querying the database will fail  

**Detection:**
- Check if database `pakwheels_db` exists in MySQL
- Check if tables (vehicles, locations, users, etc.) are present
- Verify record count in vehicles table

**Solution Steps:**
1. Connect to MySQL with root credentials from .env
2. Execute `01_create_database.sql` to create the database
3. Execute `02_create_tables.sql` to create all 12 tables with proper schema
4. Execute `03_insert_locations.sql` through `09_insert_vehicle_images.sql` to load sample data
5. Verify data integrity with `11_sample_queries.sql`

---

### **Issue #2: MySQL Connection Configuration**
**Priority:** HIGH  
**Symptoms:** OperationalError or authentication failures  
**Root Cause:** Credentials mismatch, MySQL not running, or port issues  
**Impact:** All database operations fail  

**Current Configuration (from .env):**
```
DB_HOST=localhost
DB_USER=root
DB_PASS=Muddassir12@
DB_NAME=pakwheels_db
```

**Detection:**
- Test MySQL connection manually using credentials
- Verify MySQL service is running
- Check if port 3306 is accessible
- Verify special character handling in password (`@` symbol)

**Solution Steps:**
1. Verify MySQL service is running on Windows
2. Test connection with: `mysql -h localhost -u root -pMuddassir12@ -e "SELECT 1"`
3. If fails, check MySQL logs for authentication errors
4. Ensure MySQLdb library can handle the password with special characters
5. Add retry logic in config.py if needed

---

### **Issue #3: Missing or Inconsistent Table Schema**
**Priority:** HIGH  
**Symptoms:** Column not found errors (e.g., `mileage` vs `mileage_km`)  
**Root Cause:** Schema mismatch between code expectations and actual database structure  
**Impact:** Specific queries fail on column reference errors  

**Known Column Mapping (from code comments):**
- Code expects: `mileage`, `brand`, `seller_id`
- Must verify actual table structure matches

**Detection:**
- Run `DESC vehicles;` to inspect schema
- Compare column names against routes code
- Check data types and constraints

**Solution Steps:**
1. Execute database schema inspection queries
2. If schema mismatch exists, update either:
   - Database schema (preferred if possible)
   - OR update route queries to match actual schema
3. Verify all JOINs reference correct column names
4. Test each analytics endpoint individually

---

### **Issue #4: Incomplete Sample Data**
**Priority:** MEDIUM  
**Symptoms:** Queries return empty results or NULL values  
**Root Cause:** Data insertion scripts not executed or partially executed  
**Impact:** Analytics endpoints work but return incomplete results  

**Detection:**
- Check record counts: `SELECT COUNT(*) FROM vehicles;`
- Check for NULL values in critical columns
- Verify JOIN relationships exist

**Solution Steps:**
1. Verify all INSERT scripts (03-10) were executed
2. Check data integrity with sample queries
3. If data is missing, re-execute INSERT scripts
4. Verify foreign key relationships

---

### **Issue #5: Error Handling & Logging**
**Priority:** MEDIUM  
**Symptoms:** Generic "500 error" with minimal error details  
**Root Cause:** Exception messages not properly logged to console  
**Impact:** Difficult to debug issues in production  

**Current State:**
- Generic `return jsonify({"error": str(e)}), 500` in all routes
- Error details lost or not visible

**Solution Steps:**
1. Add logging to config.py to log connection attempts
2. Add detailed exception logging in each route
3. Log SQL queries that fail
4. Create a centralized error handler
5. Add request/response logging middleware

---

### **Issue #6: Connection Management**
**Priority:** LOW  
**Symptoms:** Connection leaks, slow queries, connection timeouts  
**Root Cause:** No connection pooling, manual close calls in each route  
**Impact:** Performance degradation under load  

**Current State:**
- Each route creates a new connection: `conn = get_db()`
- Manual close in each route: `conn.close()`
- No pooling, no timeout handling

**Solution Steps:**
1. (For now) Ensure all routes properly close connections
2. Later: Implement connection pooling with SQLAlchemy
3. Add connection timeout parameters
4. Implement retry logic for transient failures

---

## Implementation Order (Recommended)

1. **Verify MySQL Service** - 5 minutes
2. **Test Database Connection** - 5 minutes  
3. **Initialize Database Schema** - 2 minutes
4. **Load Sample Data** - 2 minutes
5. **Verify Data Integrity** - 5 minutes
6. **Test All Endpoints** - 10 minutes
7. **Improve Error Logging** - 10 minutes
8. **Fix Any Remaining Query Errors** - 15 minutes

**Total Estimated Time:** ~50 minutes

---

## Success Criteria

✅ All endpoints return 200 OK  
✅ Analytics endpoints return valid JSON data  
✅ Error messages are descriptive and logged  
✅ Database operations are fast (<500ms)  
✅ All 12 tables are properly populated  
✅ JOINs work correctly across all endpoints  

---

## Files Involved

**Configuration:**
- [backend/config.py](backend/config.py) - MySQL connection handler
- [backend/.env](backend/.env) - Credentials
- [backend/app.py](backend/app.py) - Flask setup

**Routes (Database Queries):**
- [backend/routes/analytics.py](backend/routes/analytics.py) - Failing endpoints
- [backend/routes/filters.py](backend/routes/filters.py) - Filter queries
- [backend/routes/listings.py](backend/routes/listings.py) - Listing queries
- [backend/routes/search.py](backend/routes/search.py) - Search queries

**Database Scripts:**
- [database/sql_files/01_create_database.sql](database/sql_files/01_create_database.sql)
- [database/sql_files/02_create_tables.sql](database/sql_files/02_create_tables.sql)
- [database/sql_files/03-09_insert_*.sql](database/sql_files/) - Data insertion
- [database/sql_files/11_sample_queries.sql](database/sql_files/11_sample_queries.sql) - Verification

---

## Risk Assessment

| Issue | Risk Level | Mitigation |
|-------|-----------|-----------|
| Database not created | CRITICAL | Execute SQL scripts immediately |
| Credentials incorrect | CRITICAL | Test connection manually |
| Schema mismatch | HIGH | Inspect schema, update code if needed |
| Missing data | MEDIUM | Re-run INSERT scripts |
| Poor error logging | MEDIUM | Add logging for future debugging |
| Connection leaks | LOW | Currently acceptable, monitor |

---

**Next Steps:** Begin Issue #1 verification - Check if database exists and is initialized.
