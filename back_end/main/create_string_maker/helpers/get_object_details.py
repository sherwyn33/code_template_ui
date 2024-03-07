
skip_words = [
    "import",
    "#", "'''", '"""',   # Python
    "//", "/*", "*/", "*" ,  # Java & C#
    "///" ,              # C# XML Documentation comment
    "package", "namespace",
]
title = ["orders", "order"]

title2 = ["employee"]

paragraph = """import nz.co.bnz.marginchange.app.loans.DataAccessException;
import javax.inject.Inject;
import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.Date;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Optional;

    public class OrderDaoImpl implements OrderDao 
{
    private final DataSource ds;
    @Inject
    public OrderDaoImpl(DataSource ds)
    {
        this.ds = ds;
    }

    @Override
    public Order GetOrder(int id) {
        String sql = "Select OrderID, OrderDate, CustomerID, ProductID, Quantity, Price, Discount "
 + "FROM Orders WHERE ProductID=?";
                try (Connection conn = ds.getConnection() ;
             PreparedStatement stmt = conn.prepareStatement(sql)) {
             stmt.setInt(1, id);
            try (ResultSet rs = stmt.executeQuery()) {

                return readResultAsOrders(rs).stream().findFirst().orElse(null);
            } catch (SQLException e) {
                throw new DataAccessException(e);
            }
        }
        catch (SQLException e) {
            throw new DataAccessException(e);
        }
    }

    private List<Order> readResultAsOrders(ResultSet rs) throws SQLException {
        List<Order> result = new ArrayList<>();
        while (rs.next()) {
            Order r = Order.newBuilder()
		 .orderID(rs.getInt("OrderID"))
		 .orderDate(toLocalDateTime(rs.getTimestamp("OrderDate")))
		 .customerID(rs.getInt("CustomerID"))
		 .productID(rs.getInt("ProductID"))
		 .quantity(rs.getInt("Quantity"))
		 .price(rs.getBigDecimal("Price"))
		 .discount(rs.getBigDecimal("Discount")).build();
            result.add(r);
        }
        return result;
    }

 @Override
    public long UpdateOrder(Order command) throws SQLException { 
String sql = "Merge Orders As p "
 + "Using "
 + "(VALUES (?, ?, ?, ?, ?, ?, ?)) s "
 + "(OrderID, OrderDate, CustomerID, ProductID, Quantity, Price, Discount "
 + ") ON p.OrderId = s.OrderId "
 + "WHEN NOT MATCHED THEN  "
 + "INSERT (OrderDate, CustomerID, ProductID, Quantity, Price, Discount "
 + ") VALUES (OrderDate, CustomerID, ProductID, Quantity, Price, Discount "
 + ") WHEN MATCHED THEN Update Set OrderDate = s.OrderDate, CustomerID = s.CustomerID, ProductID = s.ProductID,  "
 + "Quantity = s.Quantity, Price = s.Price, Discount = s.Discount "
 + " Output inserted.OrderId As Id;";

         try (Connection conn = ds.getConnection()) {
            conn.setAutoCommit(false);
            try (
                    PreparedStatement stmt = conn.prepareStatement(sql)) {
                int c = 0;
                stmt.setInt(++c, command.orderID());
stmt.setTimestamp(++c, command.orderDate() != null ? Timestamp.valueOf(command.orderDate()) : null);
stmt.setInt(++c, command.customerID());
stmt.setInt(++c, command.productID());
stmt.setInt(++c, command.quantity());
stmt.setBigDecimal(++c, command.price());
stmt.setBigDecimal(++c, command.discount());

                ResultSet rs = stmt.executeQuery();
                long id;
                if (rs.next()){
                    id = rs.getLong("Id");
                }
                else {
                    conn.rollback();
                    throw new RuntimeException("");
                }
                conn.commit();
                return id;
                } catch (SQLException e) {
                conn.rollback();
                throw new RuntimeException(e);
            }
        }
    }

    private LocalDate toLocalDate(Date date)
    {
        if (date == null)
            return null;

        return date.toLocalDate();
    }

    private LocalDateTime toLocalDateTime(Timestamp localDateTime)
    {
        return localDateTime == null ? null : localDateTime.toLocalDateTime();
    }

}
"""