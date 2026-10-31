package com.howtodoinjava.peopledesk;

import java.time.LocalDate;

import org.springframework.ai.vectorstore.filter.Filter;
import org.springframework.ai.vectorstore.filter.FilterExpressionBuilder;

public final class PolicyFilters {

    private PolicyFilters() {
    }

    public static Filter.Expression forEmployee(EmployeeProfile employee, LocalDate asOf) {
        int day = FrontMatter.toNumber(asOf.toString());
        var b = new FilterExpressionBuilder();
        return b.and(
                b.and(
                        b.in("region", employee.region(), "GLOBAL"),
                        b.in("employee_type", employee.employeeType(), "ALL")),
                b.and(
                        b.lte("effective_from", day),
                        b.gte("effective_to", day)))
                .build();
    }
}
